from odoo import models, fields, api
from datetime import datetime, timedelta


class DatedTemplate(models.Model):
    _name = 'beesdoo.shift.template.dated'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    store = fields.Boolean(string="store", invisible=True)
    hour = fields.Integer(string='Hour',compute='_compute_time', store=True)

    @api.depends('date')
    def _compute_time(self):
        for record in self:
            if not record.date :
                record.hour = False
            else :
                record.hour = int(record.date.strftime('%H:%M:%S').replace(":", ""))

    @api.multi
    def name_get(self):
        data = []
        for timeslot in self:
            display_name = ''
            display_name += timeslot.template_id.name
            display_name += ', '
            display_name += str(timeslot.date)
            data.append((timeslot.id, display_name))
        return data


    def swap_shift_to_timeslot(self, list_shift):
        timeslot_rec = self.env["beesdoo.shift.template.dated"]
        first_shift = list_shift[0]
        last_template = first_shift.task_template_id
        new_template = first_shift.task_template_id
        last_date = first_shift.start_time
        new_date = first_shift.start_time

        first_timeslot = self.env["beesdoo.shift.template.dated"].new()
        first_timeslot.template_id = first_shift.task_template_id
        first_timeslot.date = first_shift.start_time
        timeslot_rec |= first_timeslot

        shift_generated_list = []
        for shift_rec in list_shift:
            shift_generated_list.append(shift_rec)

        for i in range(1, len(shift_generated_list)):
            if last_template != new_template or last_date != new_date:
                timeslot = self.env["beesdoo.shift.template.dated"].new()
                timeslot.template_id = shift_generated_list[i-1].task_template_id
                timeslot.date = shift_generated_list[i-1].start_time
                timeslot_rec |= timeslot
                new_template = shift_generated_list[i-1].task_template_id
                new_date = shift_generated_list[i-1].start_time
            last_template = shift_generated_list[i].task_template_id
            last_date = shift_generated_list[i].start_time

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
            timeslot_rec |= self.swap_shift_to_timeslot(shift_recset)
            next_planning_date = next_planning._get_next_planning_date(next_planning_date)
            last_sequence = next_planning.sequence
            next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
            next_planning = next_planning.with_context(visualize_date=next_planning_date)

        return timeslot_rec


    #TODO: show my next timeslot/use myshift_next_shift + swap_shift_to_timeslot
    @api.multi
    def my_timeslot(self, worker_id):
        shifts = worker_id.my_next_shift()
        timeslots = self.swap_shift_to_timeslot(shifts)
        return timeslots