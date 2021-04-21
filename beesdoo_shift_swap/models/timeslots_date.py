from odoo import models, fields, api
from datetime import datetime, timedelta

from odoo import _
from odoo.exceptions import UserError

class TimeslotsDate(models.Model):
    _name = 'beesdoo.shift.timeslots_date'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    #shift_id = fields.Integer(compute='compute_shift')


    def swap_shift_to_timeslot(self, list_shift):
        timeslot_rec = []
        first_shift =list_shift[0]
        last_template = first_shift.task_template_id
        new_template = first_shift.task_template_id

        first_timeslot = self.env["beesdoo.shift.timeslots_date"].new()
        first_timeslot.template_id = first_shift.task_template_id
        first_timeslot.date = first_shift.start_time
        timeslot_rec.append((first_timeslot.template_id, first_timeslot.date))

        shift_generated_list = []
        for shift_rec in list_shift:
            shift_generated_list.append(shift_rec)

        for i in range(0, len(shift_generated_list)):
            if last_template != new_template:
                timeslot = self.env["beesdoo.shift.timeslots_date"].new()
                timeslot.template_id = shift_generated_list[i].task_template_id
                timeslot.date = shift_generated_list[i].start_time
                timeslot_rec.append((timeslot.template_id, timeslot.date))
                new_template = shift_generated_list[i].task_template_id
            last_template = shift_generated_list[i].task_template_id

        shift_generated_list.clear()

        return timeslot_rec

    @api.model
    def display_timeslot(self,my_timeslot):

        start_date = datetime.now()

        #generate timeslot of the shift already generated

        shift_generated = (self.env["beesdoo.shift.shift"].sudo().search([
            ("start_time", ">", start_date.strftime("%Y-%m-%d %H:%M:%S"))
        ],
        order="start_time, task_template_id, task_type_id"))
        #timeslot_rec = []
        #timeslot_rec.append( self.swap_shift_to_timeslot(shift_generated))

        timeslot_rec = self.swap_shift_to_timeslot(shift_generated)

        # generate timeslot of the shift not generated
        last_sequence = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("last_planning_seq")
        )
        next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
        next_planning_date = fields.Datetime.from_string(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("next_planning_date", 0)
        )
        #TODO : create system parameters for end_date
        date = my_timeslot.date
        end_date = my_timeslot.date + timedelta(days=2*28)
        next_planning = next_planning.with_context(visualize_date=next_planning_date)
        shift_recset = self.env["beesdoo.shift.shift"]

        '''
        if not next_planning.task_template_ids:
            _logger.error(
                "Could not generate next planning: no task template defined."
            )
            return
        '''

        while next_planning_date < end_date :
            shift_recset = next_planning.task_template_ids._generate_task_day()
            timeslot_rec.extend(self.swap_shift_to_timeslot(shift_recset))
            next_planning_date = next_planning._get_next_planning_date(next_planning_date)
            last_sequence = next_planning.sequence
            next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
            next_planning = next_planning.with_context(visualize_date=next_planning_date)

        return timeslot_rec