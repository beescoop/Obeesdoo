from odoo import api, models


class StockPackOperation(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def actions_on_articles(self):
        ids = self._ids
        context = self._context
        ctx = (context or {}).copy()
        ctx["articles"] = []
        for line in self.browse(ids).move_line_ids:
            ctx["articles"].append(line.product_id.product_tmpl_id.id)
        if ctx["articles"]:
            return {
                "name": "Articles",
                "view_type": "list",
                "view_mode": "list",
                "res_model": "product.template",
                "view_id": False,
                "target": "current",
                "type": "ir.actions.act_window",
                "context": ctx,
                "nodestroy": True,
                "res_id": ctx["articles"],
                "domain": [("id", "in", ctx["articles"])],
            }
