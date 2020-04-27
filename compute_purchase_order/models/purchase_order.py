from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    original_cpo_id = fields.Many2one(
        'computed.purchase.order',
        string='Original CPO',
        help='CPO used to generate this Purchase Order'
    )
