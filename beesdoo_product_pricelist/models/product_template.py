from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_price = fields.Float(
        string="Purchase Price",
        compute="_compute_purchase_price",
        inverse="_inverse_purchase_price",
    )

    @api.multi
    @api.depends("seller_ids")
    def _compute_purchase_price(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            if supplierinfo:
                product.purchase_price = supplierinfo.price
            else:
                product.purchase_price = 0

    @api.multi
    def _inverse_purchase_price(self):
        for product in self:
            supplierinfo = product._get_main_supplier_info()
            if supplierinfo:
                supplierinfo.price = product.purchase_price
            else:
                raise ValidationError(
                    _("No Vendor defined for product '%s'") % product.name
                )
