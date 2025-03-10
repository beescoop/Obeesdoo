from odoo import fields, models


class ShiftTag(models.Model):
    _name = "volunteer.shift.tag"
    _description = "Shift Tag"

    name = fields.Char()
    description = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
