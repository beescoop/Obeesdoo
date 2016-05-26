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

    display_unit = fields.Many2one('product.uom')
    default_reference_unit = fields.Many2one('product.uom')
    display_weight = fields.Float(compute='_get_display_weight', store=True)

    total_with_vat = fields.Float(compute='_get_total', store=True, string="Total Sales Price with VAT")
    total_with_vat_by_unit = fields.Float(compute='_get_total', store=True, string="Total Sales Price with VAT by Reference Unit")
    total_deposit = fields.Float(compute='_get_total', store=True, string="Deposit Price")

    @api.one
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_seller_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        sellers_ids = self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)
        self.main_seller_id = sellers_ids and sellers_ids[0].name or False

    @api.one
    @api.depends('taxes_id', 'list_price', 'taxes_id.amount', 'taxes_id.tax_group_id', 'total_with_vat', 'display_weight', 'weight')
    def _get_total(self):
        consignes_group = self.env.ref('beesdoo_product.consignes_group_tax')
        tax_amount_sum = sum([tax._compute_amount(self.list_price, self.list_price) for tax in self.taxes_id if tax.tax_group_id != consignes_group])
        self.total_deposit = sum([tax._compute_amount(self.list_price, self.list_price) for tax in self.taxes_id if tax.tax_group_id == consignes_group])
        self.total_with_vat = self.list_price + tax_amount_sum
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

