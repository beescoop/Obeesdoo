# -*- coding: utf-8 -*-
from openerp import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        sale_order = super(SaleOrder, self).create(vals)
        command_contact = self.env['res.partner'].search([('email', '=', 'commande@bees-coop.be')])[0]
        # We do not need to update sale_order.mail_followers_ids, the link is automatic ?!
        self.env['mail.followers'].create({'res_model' : 'sale.order', 'res_id' : sale_order.id, 'partner_id' : command_contact.id}) 
        return sale_order