from odoo import _, api, fields, models


class Task(models.Model):

    _inherit = "beesdoo.shift.shift"

    solidarity_offer_ids = fields.One2many(
        "beesdoo.shift.solidarity.offer",
        "shift_id",
        string="Solidarity shift offer",
        default=None,
    )

    is_solidarity = fields.Boolean(
        string="Solidarity shift",
        readonly=True,
        store=True,
        compute="_compute_is_solidarity",
    )

    @api.multi
    def subscribe_shift_as_solidarity(self):
        return {
            "name": _("Solidarity shift offer wizard based on shift"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.subscribe.shift.solidarity",
            "target": "new",
        }

    @api.depends("solidarity_offer_ids")
    def _compute_is_solidarity(self):
        for rec in self:
            rec.is_solidarity = bool(rec.solidarity_offer_ids)

    def cancel_solidarity_offer(self):
        self.ensure_one()
        if self.is_solidarity:
            return self.solidarity_offer_ids[0].cancel_solidarity_offer()
        return False
