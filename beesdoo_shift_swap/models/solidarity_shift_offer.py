from datetime import datetime

from odoo import api, fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _description = "beesdoo.shift.solidarity.offer"

    def _get_selection_status(self):
        return [
            ("saved", "Saved"),
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
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

    state = fields.Selection(selection=_get_selection_status, default="saved")

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    shift_id = fields.Many2one(
        "beesdoo.shift.shift",
        compute="_compute_shift_id",
    )

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    @api.depends("tmpl_dated_id", "state")
    def _compute_shift_id(self):
        for record in self:
            if record.tmpl_dated_id and record.state == "validated":
                shift = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", "=", record.tmpl_dated_id.date),
                        ("task_template_id", "=", record.tmpl_dated_id.template_id.id),
                        ("worker_id", "=", self.worker_id.id),
                    ],
                    limit=1,
                )
                if shift:
                    record.shift_id = shift
                else:
                    record.shift_id = None
            else:
                record.shift_id = None

    def subscribe_shift_if_generated(self):
        if self.tmpl_dated_id and self.state == "saved":
            future_subscribed_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if future_subscribed_shift:
                future_subscribed_shift.is_regular = True
                future_subscribed_shift.worker_id = self.worker_id
                self.state = "validated"
                return True
        return False

    def counter(self):
        counter = 0
        for record in self:
            if record.shift_id and record.shift_id.state == "validated":
                counter += 1
        return counter

    @api.multi
    def unsubscribe_shift(self):
        if self.state == "validated":
            subscribed_solidarity_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", self.worker_id.id),
                ],
                limit=1,
            )
            if subscribed_solidarity_shift:
                subscribed_solidarity_shift.write(
                    {"is_regular": False, "worker_id": False}
                )
                return True
            return False
        return False
