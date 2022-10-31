from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    pos_order_count = fields.Integer(store=True)
