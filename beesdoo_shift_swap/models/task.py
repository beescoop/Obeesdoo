from odoo import fields, models


class Task(models.Model):

    _inherit = "beesdoo.shift.shift"

    solidarity_offer_ids = fields.One2many(
        "beesdoo.shift.solidarity.offer",
        "shift_id",
        string="Solidarity shift offer",
        default=None,
    )
