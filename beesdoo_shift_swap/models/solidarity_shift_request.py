from datetime import datetime

from odoo import api, fields, models


class SolidarityShiftRequest(models.Model):
    _name = "beesdoo.shift.solidarity.request"
    _description = "beesdoo.shift.solidarity.request"

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
        "beesdoo.shift.shift",
        compute="_compute_shift_id",
    )

    reason = fields.Text(
        string="Reason",
        default="",
    )

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    @api.depends("tmpl_dated_id")
    def _compute_shift_id(self):
        for record in self:
            if record.tmpl_dated_id and record.state == "draft":
                now = datetime.now()
                # Get the shift if it is already generated
                non_feasible_shift = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("start_time", "=", record.tmpl_dated_id.date),
                        ("task_template_id", "=", record.tmpl_dated_id.template_id.id),
                        ("worker_id", "=", record.worker_id.id),
                    ],
                    limit=1,
                )
                if non_feasible_shift:
                    record.shift_id = non_feasible_shift
                    record.shift_id.write({"is_regular": False, "worker_id": False})
                    record.state = "validated"
                else:
                    record.shift_id = None

    def counter(self):
        counter = 0
        for record in self:
            if record.state != "cancelled":
                counter -= 1
        return counter
