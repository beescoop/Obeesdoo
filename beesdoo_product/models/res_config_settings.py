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

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        select_type = self.env["ir.config_parameter"].sudo()
        suggested_price_reference = select_type.get_param(
            "beesdoo_product.suggested_price_reference"
        )
        res.update({"suggested_price_reference": suggested_price_reference})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        select_type = self.env["ir.config_parameter"].sudo()
        select_type.set_param(
            "beesdoo_product.suggested_price_reference",
            self.suggested_price_reference,
        )
