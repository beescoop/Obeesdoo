from odoo import fields, models


class ShiftTemplate(models.Model):
    _inherit = "shift.template"

    beneficiary = fields.Many2one(
        "res.partner",
        domain=[
            ("is_beneficiary", "=", True),
        ],
    )
