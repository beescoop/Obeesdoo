# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'
    
class PurchaseOrderLine(models.Model):
    
    _inherit = 'purchase.order.line'
    
    product_id = fields.Many2one('product.product', string='Product', 
                                 domain=['&',('purchase_ok', '=', True),('template.main_seller_id','=','order_id.partner_id')], change_default=True, required=True)
    
    @api.onchange('order_id')
    def _onchange_order_id(self):
        print "changed", self.order_id, self.order_id.partner_id