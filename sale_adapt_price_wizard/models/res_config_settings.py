# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    auto_write_suggested_price = fields.Boolean(
        string="Automatically write suggested price",
        help="""
        When editing the purchase price of a product (only in the 'Edit Price' menu),
        automatically set its sales price as the calculated suggested price.
        """,
        config_parameter="sale_adapt_price_wizard.auto_write_suggested_price",
        default=False,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        auto_write_suggested_price = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_adapt_price_wizard.auto_write_suggested_price")
        )
        res.update({"auto_write_suggested_price": auto_write_suggested_price})
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "sale_suggested_price.auto_write_suggested_price",
            self.auto_write_suggested_price,
        )
