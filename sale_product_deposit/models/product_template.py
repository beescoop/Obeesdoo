# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


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
    several_tax_strategies_warning = fields.Boolean(
        string="This product can't be printed from the Point"
        " of Sale because several tax strategies were defined.",
        compute="_compute_total",
        compute_sudo=True,
    )

    @api.depends(
        "taxes_id",
        "list_price",
        "taxes_id.amount",
        "taxes_id.tax_group_id",
        "uom_id",
    )
    def _compute_total(self):
        for product in self:

            product.several_tax_strategies_warning = False

            taxes_included = set(product.taxes_id.mapped("price_include"))

            if len(taxes_included) == 0:
                product.total_with_vat = product.list_price

            elif len(taxes_included) > 1:
                _logger.warning(
                    "Several tax strategies (price_include)"
                    " defined for product (%s, %s)",
                    product.id,
                    product.name,
                )
                product.several_tax_strategies_warning = True

            elif taxes_included.pop():
                product.total_with_vat = product.list_price
            else:
                tax_amount_sum = sum(
                    [
                        tax._compute_amount(product.list_price, product.list_price)
                        for tax in product.taxes_id
                    ]
                )
                product.total_with_vat = product.list_price + tax_amount_sum

            if product.deposit_product_id:
                product.total_deposit = product.deposit_product_id.lst_price
            else:
                product.total_deposit = False

            if product.uom_id.factor_inv:
                product.total_with_vat_by_unit = (
                    product.total_with_vat / product.uom_id.factor_inv
                )
