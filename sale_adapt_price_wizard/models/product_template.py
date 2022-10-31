# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    list_price_write_date = fields.Datetime(
        string="Sales Price Last Updated On",
        default=fields.Datetime.now,
        readonly=True,
    )

    def write(self, vals):
        if (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_adapt_price_wizard.auto_write_suggested_price")
        ):
            purchase_price = vals.get("purchase_price")
            if purchase_price and purchase_price != self.purchase_price:
                # force update of purchase_price (which actually modifies the
                # suppliers’ price) to ensure that the next computations that
                # depend on it are correct. there are 3 things to do:
                # 1. set value in cache
                with self.env.do_in_draft():
                    self.purchase_price = purchase_price
                # 2. call inverse compute method
                self._inverse_purchase_price()
                # 3. remove the value from vals, to avoid the process to happen a
                #    second time
                del vals["purchase_price"]

                # Important note: The list price is _only_ changed here if the
                # `purchase_price` field of the product is changed. If the
                # `price` field of the supplierinfo changes normally, the list price
                # here is NOT automatically affected.
                self.adapt_list_price(vals)

        list_price = vals.get("list_price")
        if list_price and list_price != self.list_price:
            vals["list_price_write_date"] = fields.Datetime.now()

        super().write(vals)

    @api.multi
    def adapt_list_price(self, vals, suggested_price=None):
        self.ensure_one()
        if suggested_price is None:
            suggested_price = self.suggested_price
        vals.setdefault("list_price", suggested_price)
