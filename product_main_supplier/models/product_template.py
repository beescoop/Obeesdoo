# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_seller_id = fields.Many2one(
        "res.partner",
        string="Main Seller",
        compute="_compute_main_seller_id",
        store=True,
    )

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_seller_id(self):
        for product in self:
            # todo english code Calcule le vendeur associé qui a la date de
            #  début la plus récente et plus petite qu’aujourd’hui fixme
            #   could product.main_seller_id be used instead? it seems that
            #   “seller” and “supplier” are used interchangeably in this
            #   class. is this on purpose?
            sellers_ids = product._get_main_supplier_info()
            product.main_seller_id = sellers_ids and sellers_ids[0].name or False

    def _get_main_supplier_info(self):
        # fixme this function either returns a supplier or a collection.
        #  wouldn’t it be more logical to return a supplier or None?

        # supplierinfo w/o date_start come first
        def sort_date_first(seller):
            if seller.date_start:
                return seller.date_start
            else:
                return date.max

        suppliers = self.seller_ids.sorted(key=sort_date_first, reverse=True)
        if suppliers:
            return suppliers[0]
        else:
            return suppliers
