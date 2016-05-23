 # -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import UserError

class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'delivery')])

    main_seller_id = fields.Many2one('res.partner', compute='_compute_main_seller_id', store=True)

    display_unit = fields.Many2one('product.uom', required=True, default=lambda self: self.env.ref('product.product_uom_kgm'))
    default_reference_unit = fields.Many2one('product.uom', required=True, default=lambda self: self.env.ref('product.product_uom_kgm'))
    display_weight = fields.Float(compute='_get_display_weight', store=True)

    total_with_vat = fields.Float(compute='_get_total_with_vat', store=True)
    total_with_vat_by_unit = fields.Float(compute='_get_total_with_vat_by_unit', store=True)

    @api.one
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_seller_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        sellers_ids = self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)
        self.main_seller_id = sellers_ids and sellers_ids[0].name or False

    @api.one
    @api.depends('taxes_id', 'list_price')
    def _get_total_with_vat(self):
        tax_amount_sum = sum([tax.amount for tax in self.taxes_id])
        self.total_with_vat = self.list_price * (100.0 + tax_amount_sum) / 100

    @api.one
    @api.depends('total_with_vat', 'display_weight', 'weight')
    def _get_total_with_vat_by_unit(self):
        print self.display_weight, self.total_with_vat, self.weight
        if self.display_weight > 0:
            self.total_with_vat_by_unit = self.total_with_vat / self.weight

    @api.one
    @api.depends('weight', 'display_unit')
    def _get_display_weight(self):
        self.display_weight = self.weight * self.display_unit.factor

    @api.one
    @api.constrains('display_unit', 'default_reference_unit')
    def _unit_same_category(self):
        if self.display_unit.category_id != self.default_reference_unit.category_id:
            raise UserError(_('Reference Unit and Display Unit should belong to the same category'))

class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection([('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()

