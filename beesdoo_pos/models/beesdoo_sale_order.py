# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id', string='Followers',
        domain=lambda self: [('res_model', '=', self._name)])
