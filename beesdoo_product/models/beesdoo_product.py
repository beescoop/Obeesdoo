 # -*- coding: utf-8 -*-
from openerp import models, fields, api

class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'delivery')])
    
    main_seller_id = fields.Many2one('res.partner', compute='_compute_main_seller_id', store=True)
    
    @api.one
    @api.depends('seller_ids')
    def _compute_main_seller_id(self):
        # Ce champs doit être champs calculé qui va chercher 
        # le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        self.main_seller_id = sorted(self.seller_ids, key=lambda seller: seller.date_start, reverse=True)[0].name
        
    
        
class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection([('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()

