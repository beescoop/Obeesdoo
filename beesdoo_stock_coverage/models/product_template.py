# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    @api.constrains("computation_range")
    def _check_computation_range(self):
        for template in self:
            if template.computation_range <= 0:
                raise ValidationError(
                    _("Computation range must be greater than 0.")
                )

    computation_range = fields.Integer("Computation range (days)", default=14)
    range_sales = fields.Float(
        string="Sales over Range",
        compute="_compute_stock_coverage",
        store=True,
    )
    daily_sales = fields.Float(
        string="Daily Sales", compute="_compute_stock_coverage", store=True
    )
    stock_coverage = fields.Float(
        string="Stock Coverage (days)",
        compute="_compute_stock_coverage",
        store=True,
    )

    @api.multi
    @api.depends("computation_range", "virtual_available", "active")
    def _compute_stock_coverage(self):
        query = """
        select template.id  as product_template_id,
               sum(pol.qty) as total_sales,
               sum(pol.qty) / template.computation_range as daily_sales
        from pos_order_line pol
                 join pos_order po ON pol.order_id = po.id
                 join product_product product ON pol.product_id = product.id
                 join product_template template
                  ON product.product_tmpl_id = template.id
        where po.state in ('done', 'invoiced', 'paid')
          and template.active
          and po.date_order
            BETWEEN now() - template.computation_range * interval '1 days'
            and now()
            and template.id in %(template_ids)s
        group by product_template_id
        """

        if self.ids:  # on RecordSet
            template_ids = tuple(self.ids)
        elif self._origin:  # on temporary object (on_change)
            template_ids = (self._origin.id,)
        else:  # on temporary object (creation)
            return True

        self.env.cr.execute(query, {"template_ids": template_ids})
        results = {pid: (qty, avg) for pid, qty, avg in self.env.cr.fetchall()}
        for template in self:
            qty, avg = results.get(template.id, (0, 0))
            template.range_sales = qty
            template.daily_sales = avg
            if avg != 0:
                template.stock_coverage = template.virtual_available / avg
            else:
                template.stock_coverage = 9999

    @api.model
    def cron_compute_stock_coverage(self):
        templates = self.env["product.template"].search([])
        templates._compute_stock_coverage()
