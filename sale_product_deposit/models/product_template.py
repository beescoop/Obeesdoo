# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    total_with_vat = fields.Float(
        compute="_compute_total",
        store=True,
        string="Total Sales Price with VAT",
    )
    total_with_vat_by_unit = fields.Float(
        compute="_compute_total",
        store=True,
        string="Total Sales Price with VAT by Reference Unit",
    )
    total_deposit = fields.Float(
        compute="_compute_total", store=True, string="Deposit Price"
    )

    @api.depends(
        "deposit_product_id.lst_price",
        "list_price",
        "taxes_id.active",
        "taxes_id.amount",
        "taxes_id.tax_group_id",
        "weight",
    )
    def _compute_total(self):
        deposit_group = self.env.ref(
            "sale_product_deposit.deposit_tax_group", raise_if_not_found=False
        )
        for product in self:
            total_tax_incl = product.taxes_id.filtered(
                lambda t: t.tax_group_id != deposit_group
            ).compute_all(product.list_price)["total_included"]
            product.total_with_vat = total_tax_incl

            deposit_amounts = [
                tax._compute_amount(product.list_price, product.list_price)
                for tax in product.taxes_id
                if tax.tax_group_id == deposit_group
            ]
            if product.deposit_product_id:
                deposit_amounts.append(product.deposit_product_id.lst_price)
            product.total_deposit = sum(deposit_amounts)

            if product.weight > 0:
                product.total_with_vat_by_unit = total_tax_incl / product.weight
