from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RequestSolidarityShift(models.TransientModel):
    _name = "beesdoo.shift.request.solidarity.shift"
    _description = "Request solidarity shift"

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    working_mode = fields.Selection(
        related="worker_id.working_mode",
        string="Working mode",
        store=True,
    )

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Shift",
        domain=[
            ("date", ">", datetime.now()),
        ],
    )

    reason = fields.Text(string="Reason", default="")

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "beesdoo_shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    @api.onchange("worker_id")
    def _get_template_dated(self):
        for record in self:
            if record.working_mode == "irregular":
                record.tmpl_dated_id = False
            elif record.working_mode == "regular":
                # Get next dated templates
                tmpl_dated_possible = record.worker_id.get_next_tmpl_dated()
                tmpl_dated_wanted = self.env["beesdoo.shift.template.dated"]
                for template in tmpl_dated_possible:
                    tmpl_dated_wanted |= tmpl_dated_wanted.create(
                        {
                            "template_id": template.template_id.id,
                            "date": template.date,
                            "store": False,
                        }
                    )

                status = record.worker_id.cooperative_status_ids
                if status.sr + status.sc < 0:
                    # Get past absent shifts
                    absent_states = self.env["shift.shift"].get_absent_state()
                    past_shift_possible = self.env["shift.shift"].search(
                        [
                            ("worker_id", "=", record.worker_id.id),
                            ("state", "in", absent_states),
                        ],
                    )
                    for shift in past_shift_possible:
                        tmpl_dated_wanted |= tmpl_dated_wanted.create(
                            {
                                "template_id": shift.task_template_id.id,
                                "date": shift.start_time,
                                "store": False,
                            }
                        )

                return {
                    "domain": {"tmpl_dated_id": [("id", "in", tmpl_dated_wanted.ids)]}
                }

    @api.multi
    def create_request(self):
        self._check()
        if self.tmpl_dated_id:
            self.tmpl_dated_id.store = True
        self.env["beesdoo.shift.template.dated"].search(
            [("store", "=", False)]
        ).unlink()
        data = {
            "worker_id": self.worker_id.id,
            "tmpl_dated_id": self.tmpl_dated_id.id,
            "reason": self.reason,
        }
        self.env["beesdoo.shift.solidarity.request"].sudo().create(data)
