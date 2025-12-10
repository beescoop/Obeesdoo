# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_supplier_taxes_factor(self):
        self.ensure_one()
        supplier_taxes = self.supplier_taxes_id.filtered(
            lambda t: t.amount_type == "percent" and t.price_include
        )
        supplier_taxes_factor = 1
        extra_included_taxes = 0
        for supplier_tax in supplier_taxes:
            if supplier_tax.include_base_amount:
                supplier_taxes_factor *= (100 + supplier_tax.amount) / 100
            else:
                extra_included_taxes += supplier_taxes_factor * (
                    supplier_tax.amount / 100
                )
        supplier_taxes_factor = 1 / (supplier_taxes_factor + extra_included_taxes)
        return supplier_taxes_factor

    def _compute_cost_from_main_supplier_price(self):
        for rec in self:
            if (
                rec.categ_id.property_cost_method != "standard_from_main_supplier_price"
                or rec.product_variant_count != 1
                or not rec.main_supplierinfo_id
            ):
                continue
            supplier_taxes_factor = rec._compute_supplier_taxes_factor()
            uom_factor = rec.uom_po_id.factor / rec.uom_id.factor
            rec.product_variant_id.standard_price = (
                rec.main_supplierinfo_id.price * uom_factor * supplier_taxes_factor
            )

    @api.model_create_multi
    def create(self, vals_list):
        # same remark as in product.supplierinfo.write()
        recs = super().create(vals_list)
        recs._compute_cost_from_main_supplier_price()
        return recs

    def write(self, vals):
        # same remark as in product.supplierinfo.write()
        need_compute_cost = (
            "uom_po_id" in vals or "uom_id" in vals or "supplier_taxes_id" in vals
        )
        res = super().write(vals)
        if need_compute_cost:
            self._compute_cost_from_main_supplier_price()
        return res
