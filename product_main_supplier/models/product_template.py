# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import datetime

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        compute="_compute_main_supplierinfo_id",
        store=True,
    )
    # main_seller_id is used as there exist a seller_ids that
    # links to all the supplierinfo_ids
    main_seller_id = fields.Many2one(
        string="Main Seller",
        comodel_name="res.partner",
        related="main_supplierinfo_id.name",
        store=True,
    )
    main_seller_id_product_code = fields.Char(
        string="Main Seller Product Code",
        related="main_supplierinfo_id.product_code",
        store=True,
    )
    main_seller_id_price = fields.Float(
        string="Supplier Price",
        related="main_supplierinfo_id.price",
    )
    main_seller_id_minimum_qty = fields.Float(
        string="Minimum Quantity", related="main_supplierinfo_id.min_qty"
    )

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_supplierinfo_id(self):
        for product in self:
            product.main_supplierinfo_id = product._get_main_supplier_info()

    def _get_main_supplier_info(self):
        """Return the main supplierinfo linked to this product.

        The main supplierinfo is the most recent one based on the
        supplierinfo.date_start. If date_start is empty then the
        supplier is considered to be the most recent one.

        If there is no supplierinfo then it returns an empty recordset.
        """
        self.ensure_one()

        # supplierinfo w/o date_start come first
        def sort_date_asc(seller):
            if seller.date_start:
                return seller.date_start
            else:
                return datetime.date.max

        suppliers = self.seller_ids.sorted(key=sort_date_asc, reverse=True)
        if suppliers:
            return suppliers[0]
        else:
            return suppliers
