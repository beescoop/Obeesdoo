# -*- coding: utf8 -*-
from datetime import datetime
from itertools import groupby
from openerp import http
from openerp.http import request

from openerp.addons.beesdoo_shift.models.planning import float_to_time

class WebsiteShiftController(http.Controller):

    @http.route('/shift_irregular_worker', auth='public', website=True)
    def shift_irregular_worker(self, **kwargs):
        # Get all the shifts in the future with no worker
        now = datetime.now()
        shifts = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
             ('worker_id', '=', False)],
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

        shifts_and_count = []
        nb_displayed_shift = 0 # Number of shift displayed
        for (keys, grouped_shifts) in groupby_iter:
            (task_template, _, _) = keys
            nb_displayed_shift = nb_displayed_shift + 1
            s = list(grouped_shifts)
            free_space = len(s)
            if free_space >= task_template.worker_nb * hide_rule:
                shifts_and_count.append([free_space, s[0]])
            # Stop showing shifts if the limit is reached
            if irregular_shift_limit > 0 and nb_displayed_shift >= irregular_shift_limit:
                break

        return request.render(
            'beesdoo_website_shift.shift_template',
            {
                'shift_templates': shifts_and_count,
                'highlight_rule': highlight_rule,
            }
        )

    @http.route('/shift_template_regular_worker', auth='public', website=True)
    def shift_template_regular_worker(self, **kwargs):
        # Get all the task template
        template = request.env['beesdoo.shift.template']
        task_templates = template.sudo().search([], order="planning_id, day_nb_id, start_time")

        return request.render('beesdoo_website_shift.task_template',
            {
                'task_templates': task_templates,
                'float_to_time': float_to_time
            }
        )
