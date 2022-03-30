import math
from datetime import datetime

from odoo import fields, models


def float_to_time(f):
    decimal, integer = math.modf(f)
    return "{}:{}".format(
        str(int(integer)).zfill(2), str(int(round(decimal * 60))).zfill(2)
    )


class SolidarityShiftRequest(models.Model):
    _name = "beesdoo.shift.solidarity.request"
    _description = "beesdoo.shift.solidarity.request"

    def _get_selection_status(self):
        return [
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ]

    def _get_personal_counter_status(self):
        return [
            ("not_modified", "Not modified"),
            ("request_ok", "Request OK"),
            ("cancel_ok", "Cancel OK"),
        ]

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
    )

    state = fields.Selection(selection=_get_selection_status, default="validated")

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    reason = fields.Text(string="Reason", default="")

    personal_counter_status = fields.Selection(
        selection=_get_personal_counter_status, default="not_modified"
    )

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def unsubscribe_shift_if_generated(self):
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
        if self.tmpl_dated_id and self.state == "validated":
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

    def update_personal_counter(self):
        worker = self.worker_id
        if worker:
            if worker.working_mode == "irregular":
                if (
                    self.state == "validated"
                    and self.personal_counter_status == "not_modified"
                ):
                    worker.cooperative_status_ids[0].sr += 1
                    self.personal_counter_status = "request_ok"
                elif (
                    self.state == "cancelled"
                    and self.personal_counter_status == "request_ok"
                ):
                    worker.cooperative_status_ids[0].sr -= 1
                    self.personal_counter_status = "cancel_ok"
            return True
        return False

    def button_cancel_solidarity_request(self):
        if self.state == "validated":
            self.subscribe_shift_if_generated()
            self.state = "cancelled"
            self.update_personal_counter()

    def counter(self):
        counter = 0
        for record in self:
            if record.state == "validated":
                counter -= 1
        return counter
