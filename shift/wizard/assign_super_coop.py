from odoo import fields, models


class AssignSuperCoop(models.TransientModel):
    _name = "shift.assign_super_coop"
    _description = "shift.assign_super_coop"

    super_coop_id = fields.Many2one(
        "res.users",
        "New Super Cooperative",
        required=True,
        domain=[("super", "=", True)],
    )
    shift_ids = fields.Many2many(
        "shift.shift",
        readonly=True,
        default=lambda self: self._context.get("active_ids"),
    )

    def write_super_coop(self):
        self.ensure_one()
        self.shift_ids.write({"super_coop_id": self.super_coop_id.id})
