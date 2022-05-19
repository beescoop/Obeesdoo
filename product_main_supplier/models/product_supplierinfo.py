# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models
from odoo.tools import float_compare


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    price_write_date = fields.Datetime(
        string="Price Last Updated On",
        default=fields.Datetime.now,
        readonly=True,
    )

    def write(self, vals):
        price = vals.get("price")
        precision = self.env["decimal.precision"].precision_get("Product Price")
        if price and float_compare(price, self.price, precision) != 0:
            vals["price_write_date"] = fields.Datetime.now()
        return super().write(vals)
