# -*- encoding: utf-8 -*-
from openerp import models, fields, api
import datetime as dt


class ProductTemplate(models.Model):
    _inherit = "product.template"

    consumption_calculation_method = fields.Selection(
        selection=[('sales_history', 'Sales History')],
        string='Consumption Calculation Method',
        default='sales_history',
    )
    calculation_range = fields.Integer(
        'Calculation range (days)',
        default=365,
    )

    average_consumption = fields.Float(
        string='Average consumption',
        compute='_compute_average_daily_consumption',
        digits=(100, 2),
    )
    total_consumption = fields.Float(
        string='Total consumption',
        compute='_compute_total_consumption',
        # store=True,
    )

    @api.multi
    @api.depends('total_consumption')
    def _compute_average_daily_consumption(self):
        for template in self:
            if template.calculation_range > 0:
                avg = template.total_consumption / template.calculation_range
            else:
                avg = 0
            template.average_consumption = avg

        return True

    @api.depends('calculation_range')
    @api.multi
    def _compute_total_consumption(self):
        for template in self:
            products = (
                self.env['product.product']
                    .search([('product_tmpl_id', '=', template.id)]))
            products_id = products.mapped('id')

            today = dt.date.today()
            pol_date_limit = today - dt.timedelta(days=template.calculation_range)

            order_lines = (
                self.env['pos.order.line']
                    .search([
                        ('product_id', 'in', products_id),
                        ('create_date', '>', fields.Datetime.to_string(pol_date_limit))
                ])
            )

            if len(order_lines) > 0:
                res = sum(order_lines.mapped('qty'))
            else:
                res = 0
            template.total_consumption = res
        return True

    @api.multi
    def _compute_stock_coverage(self):
        for template in self:
            template.stock_coverage = 7.1
        return True
