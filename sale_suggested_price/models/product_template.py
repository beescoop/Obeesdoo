# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    suggested_price = fields.Float(
        string="Suggested Price",
        compute="_compute_suggested_price",
        readonly=True,
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

    purchase_price_write_date = fields.Datetime(
        string="Purchase Price Last Updated On",
        compute="_compute_purchase_price_write_date",
        readonly=True,
    )

    @api.multi
    def calculate_suggested_price(self, price=None):
        self.ensure_one()
        suggested_price_reference = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_suggested_price.suggested_price_reference")
        )
        supplier = self.main_supplierinfo_id
        if not supplier:
            raise ValueError(_("No supplier found for product {}").format(self.id))
        if price is None:
            price = supplier.price
        product_category = supplier.product_tmpl_id.categ_id
        supplier_taxes = self.supplier_taxes_id.filtered(
            lambda t: t.amount_type == "percent" and t.price_include
        )
        supplier_taxes_factor = 1 / (1 + sum(supplier_taxes.mapped("amount")) / 100)
        sale_taxes = self.taxes_id.filtered(
            lambda t: t.amount_type == "percent" and t.price_include
        )
        sale_taxes_factor = 1 + sum(sale_taxes.mapped("amount")) / 100
        profit_margin_supplier = supplier.name.profit_margin
        profit_margin_product_category = product_category.profit_margin
        profit_margin = profit_margin_supplier or profit_margin_product_category
        profit_margin_factor = (
            1 / (1 - profit_margin / 100)
            if suggested_price_reference == "sale_price"
            else (1 + profit_margin / 100)
        )

        # price of purchase is given for uom_po_id
        #   suggested *sale* price must be adapted to uom_id
        uom_factor = self.uom_po_id.factor / self.uom_id.factor

        suggested_price = (
            price
            * uom_factor
            * supplier_taxes_factor
            * sale_taxes_factor
            * profit_margin_factor
        )

        if product_category.should_round_suggested_price:
            suggested_price = product_category._round(suggested_price)

        return suggested_price

    @api.multi
    @api.depends("seller_ids")
    def _compute_purchase_price(self):
        for product in self:
            supplierinfo = product.main_supplierinfo_id
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
        for product in self:
            try:
                product.suggested_price = product.calculate_suggested_price()
            except ValueError:
                pass

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

    @api.multi
    @api.depends("purchase_price", "seller_ids")
    def _compute_purchase_price_write_date(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            product.purchase_price_write_date = supplierinfo.price_write_date
