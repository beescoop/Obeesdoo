from odoo import fields, models


class Company(models.Model):
    _inherit = "res.company"

    member_card_logo = fields.Binary(attachment=True, readonly=False)
