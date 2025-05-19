# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _compute_cost_from_main_supplier_price(self):
        for rec in self:
            if (
                rec.categ_id.property_cost_method != "standard_from_main_supplier_price"
                or rec.product_variant_count != 1
            ):
                continue
            uom_factor = rec.uom_po_id.factor / rec.uom_id.factor
            rec.product_variant_id.standard_price = (
                rec.main_supplierinfo_id.price * uom_factor
            )

    def write(self, vals):
        # same remark as in product.supplierinfo.write()
        need_compute_cost = "uom_po_id" in vals or "uom_id" in vals
        res = super().write(vals)
        if need_compute_cost:
            self._compute_cost_from_main_supplier_price()
        return res
