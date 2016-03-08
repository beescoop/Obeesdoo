# -*- coding: utf-8 -*-
from openerp import models, fields, api
from random import randint

class MemberCard(models.Model):
    
    def _get_current_user(self):
        return self.env.uid
    
    def _get_current_client(self):
        # TODO : this does not work
        return self.env['res.partner'].search([('id', '=',self.env.context['active_id'])])
    
    def _compute_bar_code(self):
        rule = self.env['barcode.rule'].search([('name', '=', 'Customer Barcodes')])[0]
        nomenclature = self.env['barcode.nomenclature']
        size = 13-len(rule.pattern)
        ean = rule.pattern + str(randint(10**(size-1), 10**size-1))
        code = ean[0:12] + str(nomenclature.ean_checksum(ean))
        nomenclature.check_encoding(code,'ean13')
        return code
    
    _name = 'member.card'
    _order = 'activation_date desc'
    
    valid = fields.Boolean(default=True, string="Active")
    barcode = fields.Char('Barcode', oldname='ean13', default=_compute_bar_code)
    partner_id = fields.Many2one('res.partner') #, default=_get_current_client)
    responsible_id = fields.Many2one('res.users', default=_get_current_user)
    activation_date = fields.Date(default=fields.Date.today, readonly=True)
    end_date = fields.Date(readonly=True)
    comment = fields.Char("Raison", required=True)
    
# A transient model for the creation of a new card. The user can only define the raison why 
# a new card is needed and the eater/worker that is concerned.
class BeesMemberCardWizard(models.TransientModel):
    _name = 'beesmembercard.wizard'
   
    new_comment = fields.Char('Raison', required=True)
    
    @api.multi
    def create_new_card(self):
        client = self.env['res.partner'].search([('id', '=',self.env.context['active_id'])])
        client._deactivate_active_cards()
        client._new_card(self.new_comment)

