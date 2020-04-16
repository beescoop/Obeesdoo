# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_supplier_id = fields.Many2one(
        'res.partner',
        compute='_compute_main_supplier_id',
        store=True
    )

    def _get_sorted_supplierinfo(self):
        return self.seller_ids.sorted(
            key=lambda seller: seller.date_start,
            reverse=True)

    @api.multi
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_supplier_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente
        # et plus petite qu’aujourd’hui
        for pt in self:
            sellers_ids = pt._get_sorted_supplierinfo()
            pt.main_supplier_id = sellers_ids and sellers_ids[0].name or False
