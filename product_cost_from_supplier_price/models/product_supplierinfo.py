# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, models


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model_create_multi
    def create(self, vals_list):
        # same remark as in write()
        recs = super().create(vals_list)
        for rec in recs:
            if rec.product_tmpl_id.main_supplierinfo_id == rec:
                rec.product_tmpl_id._compute_cost_from_main_supplier_price()
        return recs

    def write(self, vals):
        # this has to be done here instead of setting a compute method on
        # product.product.standard_price because it is a company_dependent
        # field, which forces it to be computed by
        # Field._compute_company_dependent().
        price_in_vals = "price" in vals
        previous_main_supplier = self.product_tmpl_id.main_supplierinfo_id
        res = super().write(vals)
        product_template = self.product_tmpl_id
        current_main_supplier = product_template.main_supplierinfo_id
        if (
            current_main_supplier == self and price_in_vals
        ) or previous_main_supplier != current_main_supplier:
            product_template._compute_cost_from_main_supplier_price()
        return res

    def unlink(self):
        # same remark as in write()
        product_template = self.product_tmpl_id
        is_main_supplier = product_template.main_supplierinfo_id == self
        res = super().unlink()
        if is_main_supplier:
            product_template._compute_cost_from_main_supplier_price()
        return res
