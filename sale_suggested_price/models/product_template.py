# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    suggested_price = fields.Float(
        string="Suggested Price",
        compute="_compute_suggested_price",
        readOnly=True,
        help="""
        This field computes a suggested price based on the 'Product Margin'
        field on Partners (Vendors), if it's set, or otherwise on the 'Product
        Margin' field in Product Categories (which has a default value).
        """,
    )
    purchase_price = fields.Float(
        string="Purchase Price",
        compute="_compute_purchase_price",
        inverse="_inverse_purchase_price",
    )

    @api.multi
    @api.depends(
        "seller_ids",
        "supplier_taxes_id",
        "taxes_id",
        "uom_id",
        "uom_po_id",
        "categ_id.should_round_suggested_price",
    )
    def _compute_suggested_price(self):
        suggested_price_reference = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_suggested_price.suggested_price_reference")
        )
        for product in self:
            supplier = product._get_main_supplier_info()
            if supplier:
                price = supplier.price
                supplier_taxes = product.supplier_taxes_id.filtered(
                    lambda t: t.amount_type == "percent" and t.price_include
                )
                supplier_taxes_factor = 1 / (
                    1 + sum(supplier_taxes.mapped("amount")) / 100
                )
                sale_taxes = product.taxes_id.filtered(
                    lambda t: t.amount_type == "percent" and t.price_include
                )
                sale_taxes_factor = 1 + sum(sale_taxes.mapped("amount")) / 100
                profit_margin_supplier = supplier.name.profit_margin
                profit_margin_product_category = (
                    supplier.product_tmpl_id.categ_id.profit_margin
                )
                profit_margin = profit_margin_supplier or profit_margin_product_category
                profit_margin_factor = (
                    1 / (1 - profit_margin / 100)
                    if suggested_price_reference == "sale_price"
                    else (1 + profit_margin / 100)
                )

                # price of purchase is given for uom_po_id
                #   suggested *sale* price must be adapted to uom_id
                uom_factor = product.uom_po_id.factor / product.uom_id.factor

                product.suggested_price = (
                    price
                    * uom_factor
                    * supplier_taxes_factor
                    * sale_taxes_factor
                    * profit_margin_factor
                )
                product_category = supplier.product_tmpl_id.categ_id
                if product_category.should_round_suggested_price:
                    product.suggested_price = round_5c(product.suggested_price)

    @api.multi
    @api.depends("seller_ids")
    def _compute_purchase_price(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            if supplierinfo:
                product.purchase_price = supplierinfo.price
            else:
                product.purchase_price = 0

    @api.multi
    def _inverse_purchase_price(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            if supplierinfo:
                supplierinfo.price = product.purchase_price
            else:
                raise ValidationError(
                    _("No Vendor defined for product '%s'") % product.name
                )

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


def round_5c(price):
    return float_round(price, precision_rounding=0.05, rounding_method="HALF")
