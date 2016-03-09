# -*- coding: utf-8 -*-
from openerp import models, fields, api

class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'
    
class PurchaseOrderLine(models.Model):
    
    _inherit = 'purchase.order.line'
