from odoo import fields, models


class ShiftType(models.Model):
    _name = "volunteer.shift.type"
    _description = "Shift Type"

    name = fields.Char()
    description = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
