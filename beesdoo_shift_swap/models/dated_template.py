import logging
from datetime import datetime, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DatedTemplate(models.Model):
    _name = "beesdoo.shift.template.dated"
    _description = "A shift template with a date and an hour"

    date = fields.Datetime(required=True)
    template_id = fields.Many2one("beesdoo.shift.template")
    store = fields.Boolean(string="store", invisible=True, default=True)
    hour = fields.Integer(string="Hour", compute="_compute_hour", store=True)

    start_time = fields.Datetime(required=True, compute="_compute_time")
    end_time = fields.Datetime(required=True, compute="_compute_time")

    @api.depends("date")
    def _compute_hour(self):
        for record in self:
            if not record.date:
                record.hour = False
            else:
                record.hour = int(record.date.strftime("%H:%M:%S").replace(":", ""))

    @api.depends("date")
    def _compute_time(self):
        for rec in self:
            rec.start_time = rec.date
            rec.end_time = rec.date + timedelta(
                hours=rec.template_id.end_time - rec.template_id.start_time
            )

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

    @api.model
    def swap_shift_to_tmpl_dated(self, shift_list):
        """
        This function allow to swap "beesdoo.shift.shift" type into
        "beesdoo.shift.template.dated" type.
        :parameter shift_list: beesdoo.shift.shift recordset,
        :return: beesdoo.shift.template.dated recordset
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
        return self.swap_shift_to_tmpl_dated(shifts)

    def get_tmpl_dated_same_timeslot(self, nb_days=60):
        """
        Return all the template_dated matching time and day of self but on
        another planning, between now and nb_days days after current date.
        :param nb_days: int
        :return: beesdoo.shift.template.dated recordset
        """
        self.ensure_one()
        next_tmpl_dated = self.get_next_tmpl_dated(nb_days)
        same_timeslot_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        for template in next_tmpl_dated:
            if (
                template.template_id.day_nb_id == self.template_id.day_nb_id
                and template.template_id.start_time == self.template_id.start_time
                and template.template_id.planning_id != self.template_id.planning_id
            ):
                same_timeslot_tmpl_dated |= template
        return same_timeslot_tmpl_dated

    def get_worker_same_day_same_hour(self):
        """
        Return all regular workers that are subscribed to the timeslot
        matching the template_dated (self) but on another planning
        :return: res.partner recordset
        """
        self.ensure_one()
        templates = self.env["beesdoo.shift.template"].search(
            [
                ("day_nb_id", "=", self.template_id.day_nb_id.id),
                ("start_time", "=", self.template_id.start_time),
                ("planning_id", "!=", self.template_id.planning_id.id),
            ],
        )
        workers = self.env["res.partner"]
        for template in templates:
            for worker_id in template.worker_ids:
                workers |= worker_id
        return workers

    @api.multi
    def remove_already_subscribed_shifts(self, user):
        """
        Remove from a list of dated templates the ones that matches
        a timeslot where user is already subscribed
        :param user: res.partner
        :return: beesdoo.shift.template.dated recordset
        """
        subscribed_shifts = user.get_next_shifts()
        result = self
        for rec in self:
            for tmpl_dated in self.swap_shift_to_tmpl_dated(subscribed_shifts):
                if rec.date == tmpl_dated.date:
                    result -= rec
        return result

    @api.model
    def get_available_tmpl_dated(self, sort_date_desc=False, nb_days=60):
        """
        Return all tmpl_dated with free space between now and nb_days days
        after current date. Sort them by date if sort_date_desc is True.
        :param sort_date_desc: Boolean
        :param nb_days: Integer
        :return: beesdoo.shift.template.dated recordset
        """
        available_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        next_tmpl_dated = self.get_next_tmpl_dated(nb_days)
        for template in next_tmpl_dated:
            if template.template_id.remaining_worker > 0:
                available_tmpl_dated |= template
        if sort_date_desc:
            available_tmpl_dated = available_tmpl_dated.sorted(key=lambda r: r.date)
        return available_tmpl_dated

    @api.model
    def get_underpopulated_tmpl_dated(self, sort_date_desc=False, nb_days=60):
        """
        Return all the template_dated that are underpopulated between now
        and nb_days days after current date.
        Sort them by date if sort_date_desc is True.
        :param sort_date_desc: Boolean
        :param nb_days: Integer
        :return: beesdoo.shift.template.dated recordset
        """
        available_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        next_tmpl_dated = self.get_next_tmpl_dated(nb_days)
        min_percentage_presence = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.percentage_presence")
        )
        for template in next_tmpl_dated:
            nb_worker_wanted = template.template_id.worker_nb
            nb_worker_present = nb_worker_wanted - template.template_id.remaining_worker
            percentage_presence = (nb_worker_present / nb_worker_wanted) * 100
            if percentage_presence <= min_percentage_presence:
                available_tmpl_dated |= template

        if sort_date_desc:
            available_tmpl_dated = available_tmpl_dated.sorted(key=lambda r: r.date)

        return available_tmpl_dated
