from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("sale_ok")
    def _onchange_sale_ok(self):
        """Maintains the value of `available_in_pos` when unchecking `sale_ok`,
        by storing its value before calling parent's method,
        then assigning the stored value.
        """
        was_available = self.available_in_pos
        super(ProductTemplate, self)._onchange_sale_ok()
        if not self.sale_ok:
            self.available_in_pos = was_available
