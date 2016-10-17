# -*- coding: utf-8 -*-
from openerp import models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        purchase_order = super(PurchaseOrder, self).create(vals)
        command_contact = self.env.ref('beesdoo_base.commande_beescoop', raise_if_not_found=False)
        types = self.env['mail.message.subtype'].search(['|',('res_model','=','purchase.order'),('name','=','Discussions')])
        
        if command_contact:
            self.env['mail.followers'].create({'res_model' : 'purchase.order', 
                                               'res_id' : purchase_order.id, 
                                               'partner_id' : command_contact.id,
                                               'subtype_ids': [(6, 0, types.ids)]})
        return purchase_order