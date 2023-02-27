from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    stock_coverage = fields.Float(compute="_compute_stock_coverage", store=True)

    @api.depends("product_id")
    def _compute_stock_coverage(self):
        for purchase_order_line in self:
            if purchase_order_line.product_id:
                purchase_order_line.stock_coverage = (
                    purchase_order_line.product_id.stock_coverage
                )
            else:
                purchase_order_line.stock_coverage = False
