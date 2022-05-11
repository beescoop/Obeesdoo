import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DatedTemplate(models.Model):
    _name = "beesdoo.shift.template.dated"
    _description = "A shift template with a date and an hour"

    date = fields.Datetime(required=True)
    template_id = fields.Many2one("beesdoo.shift.template")
    store = fields.Boolean(string="store", invisible=True)
    hour = fields.Integer(string="Hour", compute="_compute_time", store=True)

    @api.depends("date")
    def _compute_time(self):
        for record in self:
            if not record.date:
                record.hour = False
            else:
                record.hour = int(record.date.strftime("%H:%M:%S").replace(":", ""))

    @api.multi
    def name_get(self):
        data = []
        for tmpl_dated in self:
            display_name = "%s, %s" % (
                tmpl_dated.template_id.name,
                fields.Date.to_string(tmpl_dated.date),
            )
            data.append((tmpl_dated.id, display_name))
        return data

    def swap_shift_to_tmpl_dated(self, shift_list):
        """
        This function allow to swap "beesdoo.shift.shift" type into
        "beesdoo.shift.template.dated" type.
        :parameter beesdoo.shift.shift recordset,
        :return beesdoo.shift.template.dated recordset
        """
        tmpl_dated_list = self.env["beesdoo.shift.template.dated"]

        last_date = None
        last_template = None
        for shift in shift_list:
            cur_date = shift.start_time
            cur_template = shift.task_template_id
            if cur_date != last_date or cur_template != last_template:
                tmpl_dated_list |= self.new(
                    {
                        "template_id": cur_template,
                        "date": cur_date,
                    }
                )
                last_date = cur_date
                last_template = cur_template

        return tmpl_dated_list

    @api.model
    def get_next_tmpl_dated(self, nb_days=60):
        """
        This function return all the template_dated between now
        and nb_days days after current date.
        :param nb_days: int
        :return: beesdoo.shift.template.dated recordset
        """
        end_date = datetime.now() + timedelta(days=nb_days)
        shifts = self.env["beesdoo.shift.planning"].get_future_shifts(end_date)
        tmpl_dated_rec = self.swap_shift_to_tmpl_dated(shifts)
        return tmpl_dated_rec

    def check_possibility_to_exchange(self, wanted_tmpl_dated, worker_id):
        my_next_tmpl_dated = worker_id.get_next_tmpl_dated()
        shift_in_day = 0
        shift_in_month = 0
        for tmpl_dated in my_next_tmpl_dated:
            if tmpl_dated.date == wanted_tmpl_dated.date:
                shift_in_day += 1
            if tmpl_dated.date.month == wanted_tmpl_dated.date.month:
                shift_in_month += 1
        if shift_in_day >= 2:
            raise UserError(_("You already have 2 shift in a day"))
        if shift_in_month >= 5:
            raise UserError(_("You already have 5 shift in a month"))

    def remove_already_subscribed_shifts(self, user):
        subscribed_shifts = user.get_next_shifts()
        result = self
        for rec in self:
            for tmpl_dated in self.swap_shift_to_tmpl_dated(subscribed_shifts):
                if rec.date == tmpl_dated.date:
                    result -= rec
        return result

    def get_available_tmpl_dated(self, sort_date_desc=False):
        available_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        next_tmpl_dated = self.get_next_tmpl_dated()
        for template in next_tmpl_dated:
            if template.template_id.remaining_worker > 0:
                available_tmpl_dated |= template
        if sort_date_desc:
            available_tmpl_dated = available_tmpl_dated.sorted(key=lambda r: r.date)
        return available_tmpl_dated
