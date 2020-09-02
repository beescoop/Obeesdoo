# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import api, fields, models


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    date_start = fields.Date(default=fields.Date.context_today, required=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_supplier_id = fields.Many2one(
        "res.partner", compute="_compute_main_supplier_id", store=True
    )

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_supplier_id(self):
        far_future = date(3000, 1, 1)

        def sort_date_first(seller):
            if seller.date_start:
                return seller.date_start
            else:
                return far_future

        for pt in self:
            sellers_ids = pt.seller_ids.sorted(
                key=sort_date_first, reverse=True
            )
            if sellers_ids:
                pt.main_supplier_id = sellers_ids[0].name
            else:
                pt.main_supplier_id = False
