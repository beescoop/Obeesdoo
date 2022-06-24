from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    max_shipping_date = fields.Datetime("End Shipping Date")

    @api.multi
    def copy_qty(self):
        self.ensure_one()
        for move_line in self.move_line_ids:
            move_line.qty_done = move_line.product_qty
        return True
