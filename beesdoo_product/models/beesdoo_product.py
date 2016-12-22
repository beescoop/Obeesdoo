 # -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import UserError
import uuid

class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain=[('type', '=', 'delivery')])

    main_seller_id = fields.Many2one('res.partner', compute='_compute_main_seller_id', store=True)

    display_unit = fields.Many2one('product.uom')
    default_reference_unit = fields.Many2one('product.uom')
    display_weight = fields.Float(compute='_get_display_weight', store=True)

    total_with_vat = fields.Float(compute='_get_total', store=True, string="Total Sales Price with VAT")
    total_with_vat_by_unit = fields.Float(compute='_get_total', store=True, string="Total Sales Price with VAT by Reference Unit")
    total_deposit = fields.Float(compute='_get_total', store=True, string="Deposit Price")

    label_to_be_printed = fields.Boolean('Print label?')
    label_last_printed = fields.Datetime('Label last printed on')

    note = fields.Text('Comments')

    # S0023 : List_price = Price HTVA, so add a suggested price
    list_price = fields.Float(string='exVAT Price')
    suggested_price = fields.Float(string='Suggested exVAT Price', compute='_compute_cost', readOnly=True)

    def _get_main_supplier_info(self):
        return self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)

    @api.one
    def generate_barcode(self):
        print 'generate barcode', self.barcode, self.barcode == ''
        rule = self.env['barcode.rule'].search([('name', '=', 'Beescoop Product Barcodes')])[0]
        size = 13 - len(rule.pattern)
        ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
        bc = ean[0:12] + str(self.env['barcode.nomenclature'].ean_checksum(ean))
        # Make sure there is no other active member with the same barcode
        while(self.search_count([('barcode', '=', bc)]) > 1):
            ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
            bc = ean[0:12] + str(self.env['barcode.nomenclature'].ean_checksum(ean))
        print 'barcode :', bc
        self.barcode = bc

    @api.one
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_seller_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        sellers_ids = self._get_main_supplier_info()  # self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)
        self.main_seller_id = sellers_ids and sellers_ids[0].name or False

    @api.one
    @api.depends('taxes_id', 'list_price', 'taxes_id.amount', 'taxes_id.tax_group_id', 'total_with_vat', 'display_weight', 'weight')
    def _get_total(self):
        consignes_group = self.env.ref('beesdoo_product.consignes_group_tax', raise_if_not_found=False)

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

    @api.one
    @api.depends('seller_ids')
    def _compute_cost(self):
        suppliers = self._get_main_supplier_info()
        if(len(suppliers) > 0):
            self.suggested_price = (suppliers[0].price * self.uom_po_id.factor)* (1 + suppliers[0].product_tmpl_id.categ_id.profit_margin / 100)

class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection([('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()

class BeesdooProductCategory(models.Model):
    _inherit = "product.category"

    profit_margin = fields.Float(default = '10.0', string = "Product Margin [%]")

    @api.one
    @api.constrains('profit_margin')
    def _check_margin(self):
        if (self.profit_margin < 0.0):
            raise UserError(_('Percentages for Profit Margin must > 0.'))

class BeesdooProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    price = fields.Float('exVAT Price')

