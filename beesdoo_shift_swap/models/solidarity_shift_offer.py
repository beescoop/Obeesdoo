from datetime import datetime

from odoo import api, fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _description = "beesdoo.shift.solidarity.offer"

    def _get_selection_status(self):
        return [
            ("draft", "Draft"),
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

    state = fields.Selection(selection=_get_selection_status, default="draft")

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_shift_already_generated"
    )

    @api.depends("tmpl_dated_id")
    def _conpute_shift_already_generated(self):
        for record in self:
            # Get current date
            now = datetime.now()
            if not record.tmpl_dated_id:
                record.shift_id = False
            elif self.state == "validated":
                record.shift_id = False
            else:
                # Get the shift if it is already generated
                future_subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("start_time", "=", record.tmpl_dated_id.date),
                        ("task_template_id", "=", record.tmpl_dated_id.template_id.id),
                        ("worker_id", "=", None),
                    ],
                    limit=1,
                )
                # check if is there a shift generated
                if future_subscribed_shifts_rec:
                    record.shift_id = future_subscribed_shifts_rec
                    return True
                return False

    def counter(self):
        counter = 0
        for record in self:
            if record.state == "validated":
                counter += 1
        return counter
