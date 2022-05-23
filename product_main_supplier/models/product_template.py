# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    main_seller_id = fields.Many2one(
        "res.partner",
        string="Main Seller",
        compute="_compute_main_seller_id",
        store=True,
    )

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_seller_id(self):
        for product in self:
            # todo english code Calcule le vendeur associé qui a la date de
            #  début la plus récente et plus petite qu’aujourd’hui fixme
            #   could product.main_seller_id be used instead? it seems that
            #   “seller” and “supplier” are used interchangeably in this
            #   class. is this on purpose?
            sellers_ids = product._get_main_supplier_info()
            product.main_seller_id = sellers_ids and sellers_ids[0].name or False
