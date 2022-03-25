from datetime import datetime

from odoo import fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _description = "beesdoo.shift.solidarity.offer"

    def _get_selection_status(self):
        return [
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
        string="Worker",
    )

    state = fields.Selection(selection=_get_selection_status, default="validated")

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    shift_id = fields.Many2one("beesdoo.shift.shift")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def subscribe_shift_if_generated(self):
        if self.tmpl_dated_id:
            future_subscribed_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if future_subscribed_shift:
                future_subscribed_shift.write(
                    {
                        "is_regular": True,
                        "worker_id": self.worker_id.id,
                        "solidarity_offer_ids": [(6, 0, self.ids)],
                    }
                )
                return True
        return False

    def unsubscribe_shift_if_generated(self):
        if self.tmpl_dated_id and self.state == "validated":
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
                    {
                        "is_regular": False,
                        "worker_id": False,
                        "solidarity_offer_ids": [(5,)],
                    }
                )
                subscribed_solidarity_shift.solidarity_offer_ids = None
                return True
        return False

    def counter(self):
        counter = 0
        for record in self:
            if record.shift_id and record.shift_id.state == "validated":
                counter += 1
        return counter
