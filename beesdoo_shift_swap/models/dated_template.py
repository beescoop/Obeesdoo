from odoo import models, fields, api,_
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

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
            display_name += fields.Date.to_string(timeslot.date)
            data.append((timeslot.id, display_name))
        return data


    def swap_shift_to_timeslot(self, list_shift):
        """
        This function allow to swap "beesdoo.shift.shift" type into
        "beesdoo.shift.template.dated" type.
        :parameter beesdoo.shift.shift recordset,
        :return beesdoo.shift.template.dated recordset
        """
        #TODO : améliorer code

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
        """
        This function return all the "timeslot_dated", between now
        and "beesdoo_shift.day_limit_swap"(parametable) day after
        "my_timeslot" date.
        :param my_timeslot: beesdoo.shift.template.dated record,
        :return: beesdoo.shift.template.dated recordset
        """
        next_swap_limit = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.day_limit_swap")
        )
        end_date = my_timeslot.date + timedelta(days=next_swap_limit)

        shifts = self.env["res.partner"].display_future_shift(end_date)

        timeslot_rec = self.swap_shift_to_timeslot(shifts)
        return timeslot_rec

    @api.multi
    def my_timeslot(self, worker_id):
        """
        Same utility as my_next_shift() but return beesdoo.shift.template.dated
        :param worker_id: res.partner record
        :return: beesdoo.shift.template.dated recordset
        """
        shifts = worker_id.my_next_shift()
        timeslots = self.env["beesdoo.shift.template.dated"]
        if shifts :
            timeslots = self.swap_shift_to_timeslot(shifts)
        return timeslots

    def check_possibility_to_exchange(self,wanted_timeslot,worker_id):
        my_next_timeslots = self.my_timeslot(worker_id)
        shift_in_day=0
        shift_in_month=0
        for timeslot in my_next_timeslots:
            if timeslot.date == wanted_timeslot.date :
                shift_in_day += 1
            if timeslot.date.month == wanted_timeslot.date.month :
                shift_in_month += 1
        if shift_in_day >= 2 :
            raise UserError(_('You already have 2 shift in a day'))
        if shift_in_month >= 5 :
            raise UserError(_('You already have 5 shift in a month'))

class TaskTemplate(models.Model):

    _inherit = "beesdoo.shift.template"

    @api.multi
    def _generate_task_day(self):
        """
        Override _generate_task_day() function to take
        into account all the exchange.
        :return: beesdoo.shift.shift new() object (not save in db)
        """
        shifts = super(TaskTemplate,self)._generate_task_day()

        #get all the exchanges
        exchanges = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search([])
        people_exchanges = self.env["beesdoo.shift.exchange"].search([])

        template={"first":None,"second": None}
        for shift in shifts :
            template["first"] = shift.task_template_id
            for exchange in exchanges :
                if shift.worker_id.name == False and exchange.confirmed_timeslot_id.template_id == shift.task_template_id and shift.start_time == exchange.confirmed_timeslot_id.date and not exchange.confirme_status:
                    if template["first"] != template["second"] :
                        updated_data = {
                            "worker_id": exchange.worker_id.id,
                            "is_regular": True,
                        }
                        shift.update(updated_data)
                        template["second"]=shift.task_template_id
                if exchange.worker_id == shift.worker_id and shift.task_template_id == exchange.exchanged_timeslot_id.template_id and shift.start_time == exchange.exchanged_timeslot_id.date and not exchange.exchange_status:
                    updated_data = {
                        "worker_id": False,
                        "is_regular": False,
                    }
                    shift.update(updated_data)
            for record in people_exchanges :
                if shift.worker_id == record.first_request_id.worker_id and record.first_request_id.exchanged_timeslot_id.template_id == shift.task_template_id and shift.start_time == record.first_request_id.exchanged_timeslot_id.date :
                    updated_data = {
                        "worker_id": record.second_request_id.worker_id.id,
                        "is_regular": True,
                    }
                    shift.update(updated_data)
                if shift.worker_id == record.second_request_id.worker_id and shift.task_template_id == record.second_request_id.exchanged_timeslot_id.template_id and shift.start_time == record.second_request_id.exchanged_timeslot_id.date :
                    updated_data = {
                        "worker_id": record.first_request_id.worker_id.id,
                        "is_regular": True,
                    }
                    shift.update(updated_data)
        return shifts