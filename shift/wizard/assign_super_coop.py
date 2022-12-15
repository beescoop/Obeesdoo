from odoo import api, fields, models


class AssignSuperCoop(models.TransientModel):
    _name = "beesddoo.shift.assign_super_coop"
    _description = "beesddoo.shift.assign_super_coop"

    super_coop_id = fields.Many2one(
        "res.users",
        "New Super Cooperative",
        required=True,
        domain=[("super", "=", True)],
    )
    shift_ids = fields.Many2many(
        "beesdoo.shift.shift",
        readonly=True,
        default=lambda self: self._context.get("active_ids"),
    )

    @api.multi
    def write_super_coop(self):
        self.ensure_one()
        self.shift_ids.write({"super_coop_id": self.super_coop_id.id})
