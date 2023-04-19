
from odoo import fields, models

class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    structure = fields.Many2one(
        "res.partner",
        domain=[
            ("is_structure", "=", True),
        ],
    )
