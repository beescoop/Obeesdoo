# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    property_cost_method = fields.Selection(
        selection_add=[
            (
                "standard_from_main_supplier_price",
                "Standard Price (From Main Supplier's Price)",
            ),
            ("fifo",),
        ],
        ondelete={"standard_from_main_supplier_price": "set standard"},
    )

    def write(self, vals):
        # same remark as in product.supplierinfo.write()
        need_compute_cost = (
            vals.get("property_cost_method") == "standard_from_main_supplier_price"
        )
        res = super().write(vals)
        if need_compute_cost:
            self.env["product.template"].search(
                [("categ_id", "=", self.id)]
            )._compute_cost_from_main_supplier_price()
        return res
