# -*- coding: utf8 -*-
from datetime import datetime
from math import floor

from openerp import http
from openerp.http import request

class ShiftPortalController(http.Controller):

    @http.route('/shift_irregular_worker', auth='public', website=True)
    def shift_irregular_worker(self, **kwargs):
        # Get all the shifts in the future with no worker
        now = datetime.now()
        shifts = request.env['beesdoo.shift.shift'].sudo().search(
            [('start_time', '>', now.strftime("%Y-%m-%d %H:%M:%S")),
            ('worker_id', '=', False)],
            order="start_time, task_template_id, task_type_id",
        )
        # Loop on all the shifts
        shift_templates = []
        current_template = None
        current_shift_template = None
        current_remaining_space = 0
        for shift in shifts:
            # For a planning id, count the number of shift that don't
            # have a worker.
            if shift.task_template_id == current_template:
                # If we are in the same template then update the number
                # of available sapce
                current_remaining_space = current_remaining_space + 1
            else:
                if current_shift_template:
                    # Save the old current_shift_template
                    current_shift_template.remaining_space = current_remaining_space
                    shift_templates.append(current_shift_template)

                # Initiate the new current_shift_template
                current_template = shift.task_template_id
                current_remaining_space = 1
                current_shift_template = ShiftTemplate(shift,
                                                       shift.start_time,
                                                       shift.end_time,
                                                       current_template.name,
                                                       current_template.task_type_id.name)

        return request.render(
            'beesdoo_portal_shift.shift_template',
            {'shift_templates': shift_templates}
        )

    @http.route('/shift_template_regular_worker', auth='public', website=True)
    def shift_template_regular_worker(self, **kwargs):
        # Get all the task template
        task_templates = request.env['beesdoo.shift.template'].sudo().search(
            [],
            order="planning_id, day_nb_id, start_time",
        )

        # Compute start_time and end_time
        task_template_times = []
        cur_start_hour = 0
        cur_start_minute = 0
        cur_end_hour = 0
        cur_end_minute = 0
        for template in task_templates:
            cur_start_hour = floor(template.start_time)
            cur_start_minute = floor((template.start_time -
                                       cur_start_hour) * 60)
            cur_end_hour = floor(template.end_time)
            cur_end_minute = floor((template.end_time -
                                       cur_end_hour) * 60)
            task_template_times.append(
                {"start_hour": "%02d" % cur_start_hour,
                 "start_minute": "%02d" % cur_start_minute,
                 "end_hour": "%02d" % cur_end_hour,
                 "end_minute": "%02d" % cur_end_minute}
            )

        return request.render(
            'beesdoo_portal_shift.task_template',
            {'task_templates': task_templates,
             'task_template_times': task_template_times}
        )


class ShiftTemplate(object):
    shift = None
    start_time = None
    end_time = None
    name = ''
    task_type = ''
    remaining_space = 0

    def __init__(self, shift, start_time, end_time, name, task_type):
        self.shift = shift
        self.start_time = start_time
        self.end_time = end_time
        self.name = name
        self.task_type = task_type
