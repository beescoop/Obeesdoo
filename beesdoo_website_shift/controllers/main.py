# -*- coding: utf8 -*-

# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# Copyright 2017-2018 Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval
from copy import copy
from datetime import datetime, timedelta
from itertools import groupby

from openerp import http, fields
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT

from openerp.addons.beesdoo_shift.models.planning import float_to_time

PERIOD = 28  # TODO: use the same constant as in 'beesdoo_shift'


class WebsiteShiftController(http.Controller):

    def is_user_irregular(self):
        user = request.env['res.users'].browse(request.uid)
        working_mode = user.partner_id.working_mode
        return working_mode == 'irregular'

    def is_user_regular(self):
        user = request.env['res.users'].browse(request.uid)
        working_mode = user.partner_id.working_mode
        return working_mode == 'regular'

    def is_user_exempted(self):
        user = request.env['res.users'].browse(request.uid)
        working_mode = user.partner_id.working_mode
        return working_mode == 'exempt'

    @http.route('/my/shift', auth='user', website=True)
    def my_shift(self, **kw):
        """
        Personal page for managing your shifts
        """
        if self.is_user_irregular():
            return request.render(
                'beesdoo_website_shift.my_shift_irregular_worker',
                self.my_shift_irregular_worker(nexturl='/my/shift')
            )
        if self.is_user_regular():
            return request.render(
                'beesdoo_website_shift.my_shift_regular_worker',
                self.my_shift_regular_worker()
            )
        if self.is_user_exempted():
            return request.render(
                'beesdoo_website_shift.my_shift_exempted_worker',
                self.my_shift_exempted_worker()
            )

        return request.render(
            'beesdoo_website_shift.my_shift_non_worker',
            {}
        )

    @http.route('/shift/<model("beesdoo.shift.shift"):shift>/subscribe', auth='user', website=True)
    def subscribe_to_shift(self, shift=None, **kw):
        """
        Subscribe the current connected user into the given shift
        This is done only if :
            * shift sign up is authorised via configuration panel
            * the current connected user is an irregular worker
            * the given shift exist
            * the shift is free for subscription
        """
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)
        # Get config
        irregular_enable_sign_up = literal_eval(request.env['ir.config_parameter'].get_param(
            'beesdoo_website_shift.irregular_enable_sign_up'))

        if (irregular_enable_sign_up
                and cur_user.partner_id.working_mode == 'irregular'
                and shift
                and not shift.worker_id):
            shift.worker_id = cur_user.partner_id
        return request.redirect(kw['nexturl'])

    @http.route('/shift_irregular_worker', auth='public', website=True)
    def public_shift_irregular_worker(self, **kw):
        """
        Show a public access page that show all the available shifts for irregular worker.
        """
        nexturl = '/shift_irregular_worker'
        irregular_enable_sign_up = False

        # Create template context
        template_context = {}
        template_context.update(self.available_shift_irregular_worker(
            irregular_enable_sign_up, nexturl
        ))

        return request.render(
            'beesdoo_website_shift.public_shift_irregular_worker',
            template_context
        )

    @http.route('/shift_template_regular_worker', auth='public', website=True)
    def public_shift_template_regular_worker(self, **kw):
        """
        Show a public access page that show all the available shift templates for regular worker.
        """
        # Get all the task template
        template = request.env['beesdoo.shift.template']
        task_templates = template.sudo().search([], order="planning_id, day_nb_id, start_time")

        return request.render(
            'beesdoo_website_shift.public_shift_template_regular_worker',
            {
                'task_templates': task_templates,
                'float_to_time': float_to_time,
            }
        )

    def my_shift_irregular_worker(self, nexturl=""):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_irregular_worker' template
        """
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)
        cur_cooperative_status = cur_user.partner_id.cooperative_status_ids

        # Get config
        irregular_enable_sign_up = literal_eval(request.env['ir.config_parameter'].get_param(
            'beesdoo_website_shift.irregular_enable_sign_up'))

        # Create template context
        template_context = {}

        template_context.update(self.my_shift_worker_status())
        template_context.update(self.my_shift_next_shifts())
        template_context.update(self.my_shift_past_shifts())
        template_context.update(self.available_shift_irregular_worker(
            irregular_enable_sign_up, nexturl
        ))

        # Compute date before which the worker is up to date
        today_date = fields.Date.from_string(cur_cooperative_status.today)
        delta = (today_date - fields.Date.from_string(cur_cooperative_status.irregular_start_date)).days
        date_before_last_shift = today_date + timedelta(days=(cur_cooperative_status.sr + 1) * PERIOD - delta % PERIOD)
        date_before_last_shift = date_before_last_shift.strftime('%Y-%m-%d')

        template_context.update(
            {
                'date_before_last_shift': date_before_last_shift,
            }
        )
        return template_context

    def my_shift_regular_worker(self):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_regular_worker' template
        """
        # Create template context
        template_context = {}

        # Get all the task template
        template = request.env['beesdoo.shift.template']
        task_templates = template.sudo().search([], order="planning_id, day_nb_id, start_time")

        template_context.update(self.my_shift_worker_status())
        template_context.update(self.my_shift_next_shifts())
        template_context.update(self.my_shift_past_shifts())
        template_context.update(
            {
                'task_templates': task_templates,
                'float_to_time': float_to_time,
            }
        )
        return template_context

    def my_shift_exempted_worker(self):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_exempted_worker' template
        """
        return self.my_shift_worker_status()

    def available_shift_irregular_worker(self, irregular_enable_sign_up=False, nexturl=""):
        """
        Return template variables for 'beesdoo_website_shift.available_shift_irregular_worker' template
        """
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)

        # Get all the shifts in the future with no worker
        now = datetime.now()
        shifts = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
             ('worker_id', '=', False)],
            order="start_time, task_template_id, task_type_id",
        )

        # Get shifts where user is subscribed
        subscribed_shifts = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
             ('worker_id', '=', cur_user.partner_id.id)],
            order="start_time, task_template_id, task_type_id",
        )

        # Get config
        irregular_shift_limit = int(request.env['ir.config_parameter'].get_param(
            'beesdoo_website_shift.irregular_shift_limit'))
        highlight_rule = int(request.env['ir.config_parameter'].get_param(
            'beesdoo_website_shift.highlight_rule'))
        hide_rule = int(request.env['ir.config_parameter'].get_param(
            'beesdoo_website_shift.hide_rule')) / 100.0

        # Grouby task_template_id, if no task_template_id is specified
        # then group by start_time, if no start_time specified sort by
        # task_type
        groupby_iter = groupby(
            shifts,
            lambda s: (s.task_template_id, s.start_time, s.task_type_id)
        )

        shifts_count_subscribed = []
        nb_displayed_shift = 0  # Number of shift displayed
        for (keys, grouped_shifts) in groupby_iter:
            (task_template, start_time, task_type) = keys
            nb_displayed_shift = nb_displayed_shift + 1
            shift_list = list(grouped_shifts)
            # Compute available space
            free_space = len(shift_list)
            # Is the current user subscribed to this task_template
            is_subscribed = any(
                (sub_shift.task_template_id == task_template and
                 sub_shift.start_time == start_time and
                 sub_shift.task_type_id == task_type)
                for sub_shift in subscribed_shifts)
            if free_space >= task_template.worker_nb * hide_rule:
                shifts_count_subscribed.append([shift_list[0], free_space, is_subscribed])
            # Stop showing shifts if the limit is reached
            if irregular_shift_limit > 0 and nb_displayed_shift >= irregular_shift_limit:
                break

        return {
            'shift_templates': shifts_count_subscribed,
            'highlight_rule': highlight_rule,
            'nexturl': nexturl,
            'irregular_enable_sign_up': irregular_enable_sign_up,
        }

    def my_shift_next_shifts(self):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_next_shifts' template
        """
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)
        # Get shifts where user is subscribed
        now = datetime.now()
        subscribed_shifts_rec = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
             ('worker_id', '=', cur_user.partner_id.id)],
            order="start_time, task_template_id, task_type_id",
        )
        # We don't use record to show the next shift as we need to add
        # fictive one for regular worker. I say 'fictive' one because
        # the next shifts for the regular worker are generated on a
        # PERIOD basis and database doesn't contain more than a PERIOD
        # of shift. So a regular worker will always see only one
        # next shift, the one that is generated and stored in the
        # database. Meaning that if we want to show the next shifts
        # for an entire year, we need to compute the dates for the next
        # shifts and create it. But we want to keep it 'fictive',
        # meaning that we don't want to write them in the database.
        # So here we convert recordset into Shift object.
        subscribed_shifts = []
        for shift_rec in subscribed_shifts_rec:
            shift = Shift(shift_rec)
            subscribed_shifts.append(shift)
            # We want to keep a copy of the shift that will serve as a
            # master to create the fictive shifts.
            if shift_rec.worker_id in shift_rec.task_template_id.worker_ids:
                main_shift = shift
                main_shift_rec = shift_rec

        # In case of regular worker, we compute his fictive next shifts
        # according to the regular_next_shift_limit
        if self.is_user_regular() and subscribed_shifts and main_shift:
            # Get config
            regular_next_shift_limit = int(request.env['ir.config_parameter'].get_param(
                'beesdoo_website_shift.regular_next_shift_limit'))
            for i in range(1, regular_next_shift_limit):
                # Compute the new date for the created shift
                start_time = fields.Datetime.from_string(main_shift_rec.start_time)
                start_time = (start_time + timedelta(days=i*PERIOD)).strftime(DATETIME_FORMAT)
                # Create the fictive shift
                shift = copy(main_shift)
                shift.id = -i  # We give negative id 'caus this shift doesn't exist in database
                shift.start_day = start_time
                shift.start_date = start_time
                subscribed_shifts.append(shift)

        return {
            'is_regular': self.is_user_regular(),
            'subscribed_shifts': subscribed_shifts,
        }

    def my_shift_past_shifts(self):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_past_shifts' template
        """
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)
        # Get config
        past_shift_limit = 0
        if self.is_user_irregular():
            past_shift_limit = int(request.env['ir.config_parameter'].get_param(
                'beesdoo_website_shift.irregular_past_shift_limit'))
        if self.is_user_regular():
            past_shift_limit = int(request.env['ir.config_parameter'].get_param(
                'beesdoo_website_shift.regular_past_shift_limit'))
        # Get shifts where user was subscribed
        now = datetime.now()
        if past_shift_limit > 0:
            past_shifts = request.env['beesdoo.shift.shift'].sudo().search(
                [('start_time', '<=', now.strftime("%Y-%m-%d %H:%M:%S")),
                 ('worker_id', '=', cur_user.partner_id.id)],
                order="start_time, task_template_id, task_type_id",
                limit=past_shift_limit,
            )
        else:
            past_shifts = request.env['beesdoo.shift.shift'].sudo().search(
                [('start_time', '<=', now.strftime("%Y-%m-%d %H:%M:%S")),
                 ('worker_id', '=', cur_user.partner_id.id)],
                order="start_time, task_template_id, task_type_id",
            )

        return {
            'past_shifts': past_shifts,
        }

    def my_shift_worker_status(self):
        """
        Return template variables for 'beesdoo_website_shift.my_shift_worker_status_*' template
        """
        cur_user = request.env['res.users'].browse(request.uid)
        return {
            'status': cur_user.partner_id.cooperative_status_ids,
        }


class Shift(object):
    """
    Represent a shift with all useful information in a format that is directly printable in a template
    """

    def __init__(self, shift_rec=None):
        self.id = 0
        self._start_day = ''
        self._start_date = ''
        self._start_time = ''
        self._end_time = ''
        self.task_type_name = ''
        self.super_coop_name = ''
        self.super_coop_phone = ''
        self.super_coop_email = ''
        if shift_rec:
            self.update(shift_rec)

    def update(self, shift_rec=None):
        """ Fill in self with data in the given record"""
        if shift_rec:
            self.id = shift_rec.id
            self.start_day = shift_rec.start_time
            self.start_date = shift_rec.start_time
            self.start_time = shift_rec.start_time
            self.end_time = shift_rec.end_time
            if shift_rec.task_type_id:
                self.task_type_name = shift_rec.task_type_id.name
            if shift_rec.super_coop_id:
                self.super_coop_name = shift_rec.super_coop_id.name
                self.super_coop_phone = shift_rec.super_coop_id.phone
                self.super_coop_email = shift_rec.super_coop_id.email

    # Properties
    @property
    def start_day(self):
        return self._start_day

    @property
    def start_date(self):
        return self._start_date

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    # Setters
    @start_day.setter
    def start_day(self, datetime_str):
        self._start_day = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime('%A')

    @start_date.setter
    def start_date(self, datetime_str):
        self._start_date = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime('%d %B %Y')

    @start_time.setter
    def start_time(self, datetime_str):
        self._start_time = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime('%H:%M')

    @end_time.setter
    def end_time(self, datetime_str):
        self._end_time = datetime.strptime(datetime_str, DATETIME_FORMAT).strftime('%H:%M')

    # Deleters
    @start_day.deleter
    def start_day(self):
        del self._start_day

    @start_date.deleter
    def start_date(self):
        del self._start_date

    @start_time.deleter
    def start_time(self):
        del self._start_time

    @end_time.deleter
    def end_time(self):
        del self._end_time
