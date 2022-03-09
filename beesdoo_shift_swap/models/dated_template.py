from odoo import models, fields, api,_
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class DatedTemplate(models.Model):
    _name = 'beesdoo.shift.template.dated'
    _description = 'A shift template with a date and an hour'

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
        for tmpl_dated in self:
            display_name = ''
            display_name += tmpl_dated.template_id.name
            display_name += ', '
            display_name += fields.Date.to_string(tmpl_dated.date)
            data.append((tmpl_dated.id, display_name))
        return data


    def swap_shift_to_tmpl_dated(self, list_shift):
        """
        This function allow to swap "beesdoo.shift.shift" type into
        "beesdoo.shift.template.dated" type.
        :parameter beesdoo.shift.shift recordset,
        :return beesdoo.shift.template.dated recordset
        """
        #TODO : améliorer code

        tmpl_dated_rec = self.env["beesdoo.shift.template.dated"]
        first_shift = list_shift[0]
        last_template = first_shift.task_template_id
        new_template = first_shift.task_template_id
        last_date = first_shift.start_time
        new_date = first_shift.start_time

        first_tmpl_dated = self.env["beesdoo.shift.template.dated"].new()
        first_tmpl_dated.template_id = first_shift.task_template_id
        first_tmpl_dated.date = first_shift.start_time
        tmpl_dated_rec |= first_tmpl_dated

        shift_generated_list = []
        for shift_rec in list_shift:
            shift_generated_list.append(shift_rec)

        for i in range(1, len(shift_generated_list)):
            if last_template != new_template or last_date != new_date:
                tmpl_dated = self.env["beesdoo.shift.template.dated"].new()
                tmpl_dated.template_id = shift_generated_list[i-1].task_template_id
                tmpl_dated.date = shift_generated_list[i-1].start_time
                tmpl_dated_rec |= tmpl_dated
                new_template = shift_generated_list[i-1].task_template_id
                new_date = shift_generated_list[i-1].start_time
            last_template = shift_generated_list[i].task_template_id
            last_date = shift_generated_list[i].start_time

        shift_generated_list.clear()

        return tmpl_dated_rec

    @api.model
    def display_tmpl_dated(self):
        """
        This function return all the "template_dated", between now
        and "beesdoo_shift.day_limit_ask_for_exchange"(parametable) day after
        current date.
        :return: beesdoo.shift.template.dated recordset
        """
        ask_date_limit = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.day_limit_ask_for_exchange")
        )
        end_date = datetime.now() + timedelta(days=ask_date_limit)

        shifts = self.env["res.partner"].display_future_shift(end_date)

        tmpl_dated_rec = self.swap_shift_to_tmpl_dated(shifts)
        return tmpl_dated_rec

    @api.multi
    def my_tmpl_dated(self, worker_id):
        """
        Same utility as my_next_shift() but return beesdoo.shift.template.dated
        :param worker_id: res.partner record
        :return: beesdoo.shift.template.dated recordset
        """
        shifts = worker_id.my_next_shift()
        tmpl_dated = self.env["beesdoo.shift.template.dated"]
        if shifts :
            tmpl_dated = self.swap_shift_to_tmpl_dated(shifts)
        return tmpl_dated

    def check_possibility_to_exchange(self,wanted_tmpl_dated,worker_id):
        my_next_tmpl_dated = self.my_tmpl_dated(worker_id)
        shift_in_day=0
        shift_in_month=0
        for tmpl_dated in my_next_tmpl_dated:
            if tmpl_dated.date == wanted_tmpl_dated.date :
                shift_in_day += 1
            if tmpl_dated.date.month == wanted_tmpl_dated.date.month :
                shift_in_month += 1
        if shift_in_day >= 2 :
            raise UserError(_('You already have 2 shift in a day'))
        if shift_in_month >= 5 :
            raise UserError(_('You already have 5 shift in a month'))
