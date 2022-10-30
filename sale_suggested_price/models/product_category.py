# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.tools.translate import _


class ProductCategory(models.Model):
    _inherit = "product.category"

    # TODO: Make this default configurable?
    profit_margin = fields.Float(default="10.0", string="Product Margin [%]")
    should_round_suggested_price = fields.Boolean(
        default=False, string="Round suggested price to 5 cents?"
    )

    rounding_method = fields.Selection(
        [("HALF-UP", "Half"), ("UP", "up"), ("DOWN", "down")],
        default="HALF-UP",
    )
    rounding_precision = fields.Float(default=0.05)

    @api.multi
    @api.constrains("profit_margin")
    def _check_margin(self):
        for product in self:
            if product.profit_margin < 0.0:
                raise UserError(_("Percentages for Profit Margin must >= 0."))

    def _round(self, price):
        self.ensure_one()
        # Use default value 0.05 and "HALF_UP"
        # in case someone erase the value on the category
        # Keep default value on the field to make it explicit to the end user
        return float_round(
            price,
            precision_rounding=self.rounding_precision or 0.05,
            rounding_method=self.rounding_method or "HALF_UP",
        )
