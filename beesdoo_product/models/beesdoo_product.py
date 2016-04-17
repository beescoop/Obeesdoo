 # -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _

class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'delivery')])

    main_seller_id = fields.Many2one('res.partner', compute='_compute_main_seller_id', store=True)

    @api.one
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_seller_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        sellers_ids = self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)
        self.main_seller_id = sellers_ids and sellers_ids[0].name or False



class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection([('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()

