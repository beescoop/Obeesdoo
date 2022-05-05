import math
from datetime import datetime, timedelta

from odoo import fields, models


def float_to_time(f):
    decimal, integer = math.modf(f)
    return "{}:{}".format(
        str(int(integer)).zfill(2), str(int(round(decimal * 60))).zfill(2)
    )


class SolidarityShiftRequest(models.Model):
    _name = "beesdoo.shift.solidarity.request"
    _description = "beesdoo.shift.solidarity.request"

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
    )

    state = fields.Selection(
        [
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ],
        default="validated",
    )

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    reason = fields.Text(string="Reason", default="")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        from the shift and update the counters
        """
        res = super(SolidarityShiftRequest, self).create(vals_list)
        if res.worker_id.working_mode == "regular":
            res.unsubscribe_shift_if_generated()
        res.update_personal_counter()
        return res

    def unsubscribe_shift_if_generated(self):
        """
        Search a shift matching the data of the request. If found,
        remove the worker from it.
        :return: Boolean
        """
        if self.tmpl_dated_id:
            non_realisable_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", self.worker_id.id),
                ],
                limit=1,
            )
            if non_realisable_shift:
                non_realisable_shift.write({"is_regular": False, "worker_id": False})
                return True
        return False

    def subscribe_shift_if_generated(self):
        """
        Search an empty shift matching the data of the request. If found,
        overwrite it with the worker id and the offer id. If not, create a
        new one with the data.
        :return: Boolean
        """
        if (
            self.tmpl_dated_id
            and self.tmpl_dated_id.date > datetime.now()
            and self.state == "validated"
        ):
            template_id = self.tmpl_dated_id.template_id
            unsubscribed_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", template_id.id),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if unsubscribed_shift:
                unsubscribed_shift.write(
                    {
                        "is_regular": True,
                        "worker_id": self.worker_id.id,
                    }
                )
                return True
            nb_shift = self.env["beesdoo.shift.shift"].search_count(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", template_id.id),
                ],
            )
            if nb_shift > 0:
                data = {
                    "name": "[%s] %s %s (%s - %s) [%s]"
                    % (
                        template_id.start_date.date(),
                        template_id.planning_id.name,
                        template_id.day_nb_id.name,
                        float_to_time(template_id.start_time),
                        float_to_time(template_id.end_time),
                        nb_shift,
                    ),
                    "task_template_id": template_id.id,
                    "task_type_id": template_id.task_type_id.id,
                    "super_coop_id": template_id.super_coop_id.id,
                    "worker_id": self.worker_id and self.worker_id.id or False,
                    "is_regular": True if self.worker_id else False,
                    "start_time": template_id.start_date,
                    "end_time": template_id.end_date,
                    "state": "open",
                }
                self.env["beesdoo.shift.shift"].create(data)
                return True
        return False

    def cancel_solidarity_request(self):
        if self.state == "validated" and (
            not self.tmpl_dated_id or self.tmpl_dated_id.date > datetime.now()
        ):
            self.subscribe_shift_if_generated()
            self.state = "cancelled"
            self.update_personal_counter()
            return True
        return False

    def check_solidarity_requests_number(self, worker_id):
        nb_requests = self.sudo().search_count(
            [
                ("worker_id", "=", worker_id),
                ("state", "=", "validated"),
                ("tmpl_dated_id.date", ">", datetime.now() - timedelta(days=365)),
            ],
        )
        return nb_requests < int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.max_solidarity_requests_number")
        )

    def update_personal_counter(self):
        """
        Override this method to define the counters behaviour when
        creating and cancelling a solidarity request
        """
        return True

    def counter(self):
        """
        Count the number of solidarity requests that have been validated.
        Used in method solidarity_counter() in res.company.
        :return: Integer
        """
        counter = 0
        for record in self:
            if record.state == "validated":
                counter += 1
        return counter
