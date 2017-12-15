# -*- coding: utf8 -*-
from datetime import datetime
from itertools import groupby
from openerp import http
from openerp.http import request

from openerp.addons.beesdoo_shift.models.planning import float_to_time

class WebsiteShiftController(http.Controller):

    @http.route('/shift', auth='user', website=True)
    def shift(self, **kwargs):
        cur_user = request.env['res.users'].browse(request.uid)
        working_mode = cur_user.partner_id.working_mode
        if working_mode == 'irregular':
            return self.shift_irregular_worker()
        if working_mode == 'regular':
            return self.shift_template_regular_worker()
        if working_mode == 'exempt':
            return self.shift_exempted_worker()

        return request.render(
            'beesdoo_website_shift.shift',
            {
                'user': cur_user,
            }
        )

    @http.route('/shift/<model("beesdoo.shift.shift"):shift>/subscribe', auth='user', website=True)
    def subscribe_to_shift(self, shift=None, **kwargs):
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)
        if (cur_user.partner_id.working_mode == 'irregular'
                and shift
                and not shift.worker_id):
            shift.worker_id = cur_user.partner_id
        return request.redirect(kwargs['nexturl'])

    def shift_irregular_worker(self, **kwargs):
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
        # then group by start_time
        groupby_func = lambda s: (s.task_template_id, s.start_time, s.task_type_id)
        groupby_iter = groupby(shifts, groupby_func)

        shifts_count_subscribed = []
        nb_displayed_shift = 0 # Number of shift displayed
        for (keys, grouped_shifts) in groupby_iter:
            (task_template, start_time, task_type) = keys
            nb_displayed_shift = nb_displayed_shift + 1
            s = list(grouped_shifts)
            # Compute available space
            free_space = len(s)
            # Is the current user subscribed to this task_template
            is_subscribed = any(
                (sub_shift.task_template_id == task_template and
                 sub_shift.start_time == start_time and
                 sub_shift.task_type_id == task_type)
                for sub_shift in subscribed_shifts)
            if free_space >= task_template.worker_nb * hide_rule:
                shifts_count_subscribed.append([s[0], free_space, is_subscribed])
            # Stop showing shifts if the limit is reached
            if irregular_shift_limit > 0 and nb_displayed_shift >= irregular_shift_limit:
                break

        return request.render(
            'beesdoo_website_shift.irregular_worker',
            {
                'partner': cur_user.partner_id,
                'status': cur_user.partner_id.cooperative_status_ids,
                'shift_templates': shifts_count_subscribed,
                'highlight_rule': highlight_rule,
                'nexturl': '/shift',
                'subscribed_shifts': subscribed_shifts,
            }
        )

    def shift_template_regular_worker(self, **kwargs):
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)

        # Get all the task template
        template = request.env['beesdoo.shift.template']
        task_templates = template.sudo().search([], order="planning_id, day_nb_id, start_time")

        # Get shifts where user is subscribed
        now = datetime.now()
        subscribed_shifts = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
             ('worker_id', '=', cur_user.partner_id.id)],
            order="start_time, task_template_id, task_type_id",
        )

        return request.render(
            'beesdoo_website_shift.regular_worker',
            {
                'partner': cur_user.partner_id,
                'status': cur_user.partner_id.cooperative_status_ids,
                'task_templates': task_templates,
                'float_to_time': float_to_time,
                'subscribed_shifts': subscribed_shifts,
            }
        )

    def shift_exempted_worker(self, **kwargs):
        # Get current user
        cur_user = request.env['res.users'].browse(request.uid)

        return request.render(
            'beesdoo_website_shift.exempted_worker',
            {
                'partner': cur_user.partner_id,
                'status': cur_user.partner_id.cooperative_status_ids,
            }
        )
