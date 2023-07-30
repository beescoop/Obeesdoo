from odoo import fields, models


class Product(models.Model):
    _inherit = "product.template"

    def _is_add_to_cart_possible(self, parent_combination=None):
        self.ensure_one()
        if self.env.user._is_public():
            return False

        if self.categ_id.web_sellable:
            return super()._is_add_to_cart_possible(
                parent_combination=parent_combination
            )
        return False


class ProductCategory(models.Model):
    _inherit = "product.category"

    web_sellable = fields.Boolean(
        string="Can be sell on the e-commerce",
        help="Can be added to the cart on ecommerce if check,"
        " only visible for information otherwises",
        default=False,
    )
