# -*- coding: utf-8 -*-
from openerp import models, fields, api


class BeesdooProduct(models.Model):
    _inherit = "product.template"

    main_supplierinfo = fields.Many2one(
        'product.supplierinfo',
        string='Main Supplier Information',
        compute='_compute_main_supplierinfo'
    )
    main_price = fields.Float(
        string='Price',
        compute='_compute_main_supplierinfo',
    )
    main_minimum_qty = fields.Float(
        string='Minimum Quantity',
        compute='_compute_main_supplierinfo',
    )

    @api.multi
    @api.depends('seller_ids')
    def _compute_main_supplierinfo(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            product.main_supplierinfo = supplierinfo
            product.main_price = supplierinfo.price
            product.main_minimum_qty = supplierinfo.min_qty
