# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ProductCategory(models.Model):
    _inherit = "product.category"

    # TODO: Make this default configurable?
    profit_margin = fields.Float(default="10.0", string="Product Margin [%]")
    should_round_suggested_price = fields.Boolean(
        default=False, string="Round suggested price to 5 cents?"
    )

    @api.multi
    @api.constrains("profit_margin")
    def _check_margin(self):
        for product in self:
            if product.profit_margin < 0.0:
                raise UserError(_("Percentages for Profit Margin must >= 0."))
