# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BeesdooProduct(models.Model):
    _inherit = 'product.template'

    eco_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'delivery')])

    display_unit = fields.Many2one('product.uom', required=True)
    default_reference_unit = fields.Many2one('product.uom', required=True)

    display_weight = fields.Float(compute='get_display_weight')

    total = fields.Float(compute='get_total')
    total_with_vat = fields.Float(compute='get_total_with_vat')

    total_with_vat_by_unit = fields.Float(compute='get_total_with_vat_by_unit')

    @api.one
    @api.depends('weight', 'display_unit')
    def get_display_weight(self):
        if self.display_unit:
            self.display_weight = self.weight / self.display_unit.factor

    @api.one
    def get_total(self):
        price_ht = self.env['product.pricelist'].search([])[0].price_get(self.id, 1)[1]
        self.total = price_ht

    @api.one
    def get_total_with_vat(self):
        tax_amount_sum = 0.0
        if hasattr(self, 'taxes_id'):
            for tax in self.taxes_id:
                tax_amount_sum = tax_amount_sum + tax.amount
        self.total_with_vat = self.total * (100.0 + tax_amount_sum) / 100

    @api.one
    def get_total_with_vat_by_unit(self):
        if self.display_weight > 0:
            self.total_with_vat_by_unit = self.total_with_vat/self.display_weight


class BeesdooProductLabel(models.Model):
    _name = 'beesdoo.product.label'

    name = fields.Char()
    type = fields.Selection(
        [('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()
