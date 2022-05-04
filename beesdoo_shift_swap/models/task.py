from odoo import api, fields, models


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
        compute="_compute_is_solidarity",
    )

    @api.depends("solidarity_offer_ids")
    def _compute_is_solidarity(self):
        self.is_solidarity = True if self.solidarity_offer_ids else False
