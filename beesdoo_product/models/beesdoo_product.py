# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BeesdooProduct(models.Model):
    _inherit = 'product.template'

    eco_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'delivery')])

    display_unit = fields.Char()
    default_reference_unit = fields.Char()
    display_weight = fields.Integer(compute='get_display_weight')

    total = fields.Float(compute='get_total')
    total_with_vat = fields.Float(compute='get_total_with_vat')

    def get_display_weight(self):
        pass



    def get_total(self):
        price_ht = self.env['product.pricelist'].search([])[0].price_get(self.id, 1)[1]
        self.total = price_ht

        # grand_total_by_unit = fields.Float(compute='get_grand_total_by_unit')
        #
        # grand_total = fields.Float(compute='get_grand_total')
        #
        # def get_grand_total(self):
        #     self.grand_total = self.env['sale.order.line'] * self.price
        #
        # def get_grand_total_by_unit(self):
        #     self.grand_total_by_unit = self.grand_total * self.unit_price
        # product.supplierinfo

    def get_total_with_vat(self):
        tax_amount_sum = 0.0
        for tax in self.taxes_id:
            tax_amount_sum = tax_amount_sum + tax.amount
        self.total_with_vat = self.total * (100.0 + tax_amount_sum) / 100



class BeesdooProductLabel(models.Model):
    _name = 'beesdoo.product.label'

    name = fields.Char()
    type = fields.Selection(
        [('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()
