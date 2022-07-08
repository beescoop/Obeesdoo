# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    suggested_price_reference = fields.Selection(
        selection=[
            ("supplier_price", "On Supplier Price"),
            ("sale_price", "On Sale Price"),
        ],
        string="Suggested price reference for margin",
        help="""
            Price on which the margin is applied when computing the suggested
                sale price.
            - Margin on Supplier Price : Suggested sale price
                = supplier price * (1 + margin / 100) (default)
            - Margin on Sale Price: Suggested sale price
                = supplier price * (1 / (1 - margin / 100))
        """,
        default="supplier_price",
    )
    auto_write_suggested_price = fields.Boolean(
        string="Automatically write suggested price",
        help="""
        When editing the purchase price of a product (only in the 'Edit Price' menu),
        automatically set its sales price as the calculated suggested price.
        """,
        config_parameter="beesdoo_product.auto_write_suggested_price",
        default=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        suggested_price_reference = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_product.suggested_price_reference")
        )
        res.update({"suggested_price_reference": suggested_price_reference})
        auto_write_suggested_price = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_product.auto_write_suggested_price")
        )
        res.update({"auto_write_suggested_price": auto_write_suggested_price})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "beesdoo_product.suggested_price_reference",
            self.suggested_price_reference,
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "beesdoo_product.auto_write_suggested_price",
            self.auto_write_suggested_price,
        )
