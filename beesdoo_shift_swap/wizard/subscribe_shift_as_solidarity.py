from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftAsSolidarity(models.TransientModel):
    _name = "beesdoo.shift.subscribe.shift.solidarity"
    _description = "Subscribe to a shift as a solidarity one"

    worker_id = fields.Many2one(
        "res.partner",
        string="Cooperator",
        required=True,
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    shift_id = fields.Many2one(
        "beesdoo.shift.shift",
        string="Shift",
        default=lambda self: self.env["beesdoo.shift.shift"].browse(
            self._context.get("active_id")
        ),
        required=True,
        readonly=True,
    )

    @api.onchange("shift_id")
    def _get_possible_workers(self):
        for record in self:
            shift = self.env["beesdoo.shift.shift"].browse(
                self._context.get("active_id")
            )
            taken_shifts = self.env["beesdoo.shift.shift"].search(
                [
                    ("task_template_id", "=", shift.task_template_id.id),
                    ("start_time", "=", shift.start_time),
                    ("worker_id", "!=", False),
                ]
            )
            possible_workers = self.env["res.partner"].search(
                [
                    ("is_worker", "=", True),
                    ("working_mode", "in", ("regular", "irregular")),
                    ("state", "not in", ("unsubscribed", "resigning")),
                ]
            )
            for s in taken_shifts:
                possible_workers &= self.env["res.partner"].search(
                    [
                        ("id", "!=", s.worker_id.id),
                    ]
                )
            return {"domain": {"worker_id": [("id", "in", possible_workers.ids)]}}

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "beesdoo_shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    @api.multi
    def create_offer(self):
        self._check()
        shift = self.env["beesdoo.shift.shift"].browse(self._context.get("active_id"))
        tmpl_dated = self.env["beesdoo.shift.template.dated"].create(
            {
                "template_id": shift.task_template_id.id,
                "date": shift.start_time,
                "store": False,
            }
        )
        data = {
            "worker_id": self.worker_id.id,
            "tmpl_dated_id": tmpl_dated.id,
        }
        self.env["beesdoo.shift.solidarity.offer"].sudo().create(data)
        return {
            "name": _("Shifts"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree",
            "view_id": self.env.ref("beesdoo_shift.task_view_tree").id,
            "res_model": "beesdoo.shift.shift",
            "target": "main",
        }
