from odoo import fields, models


class Volunteer(models.Model):
    _name = "volunteer.volunteer"
    _description = "Volunteer"
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    is_regular = fields.Boolean(default=False)
