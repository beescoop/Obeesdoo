
from odoo import fields, models

class ShiftShift(models.Model):
    _inherit = "shift.shift"

    structure = fields.Many2one(
        "res.partner",
        domain=[
            ("is_structure", "=", True),
        ],
    )
