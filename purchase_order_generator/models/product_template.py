# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_supplier_id = fields.Many2one(
        "res.partner", compute="_compute_main_supplier_id", store=True
    )

    def _get_sorted_supplierinfo(self):
        return self.seller_ids.sorted(
            key=lambda seller: seller.date_start, reverse=True
        )

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_supplier_id(self):
        for pt in self:
            sellers_ids = pt.seller_ids.sorted(
                key=lambda seller: seller.date_start, reverse=True
            )
            if sellers_ids:
                pt.main_supplier_id = sellers_ids[0].name
            else:
                pt.main_supplier_id = False
