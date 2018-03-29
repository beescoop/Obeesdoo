# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
import datetime as dt

_datetimes = map(
    lambda d: d.strftime('%Y-%m-%d %H:%M:%S'),
    (dt.datetime.now() - dt.timedelta(days=d) for d in range(0, 24, 2)))

_quantities = [0.64, 6.45, 9.65, 1.76, 9.14, 3.99,
               6.92, 2.25, 6.91, 1.44, 6.52, 1.44]


class TestProductTemplate(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestProductTemplate, self).setUp(*args, **kwargs)

        # enrico_groups = [1, 2, 3, 4, 8, 9, 10, 11, 14, 18, 23,  # fixme
        #                  24, 25, 27, 28, 32, 33, 34, 35, 36, 41,
        #                  42, 43, 47, 48, 51, 52, 53, 54, 57, 59,
        #                  60, 62, 63, 64, 65, 73, 75, 76, 77]
        # # suspected_groups = [10, 35],
        #
        # user = self.env['res.users'].create({
        #     'name': 'Test user product average consumption',
        #     'login': 'testuserproductaverageconsumption',
        #     'groups_id': [(6, 0, [enrico_groups])]
        # })
        # self.env = self.env(user=user)

        test_product_template = (
            self.env['product.template']
                .create({'name': 'test product template',
                         'calculation_range': 14,
                         'consumption_calculation_method': 'sales_history',
                         })
        )

        test_product = (
            self.env['product.product']
                .create({'name': 'test product',
                         'product_tmpl_id': test_product_template.id
                         })
        )

        for date, qty in zip(_datetimes, _quantities):
            (self.env['pos.order.line']
                 .create({'create_date': date,
                          'qty': qty,
                          'product_id': test_product.id
                          })
             )

        self.test_product_template_id = test_product_template.id
        return result

    def test_create(self):
        """Create a simple product template"""
        Template = self.env['product.template']
        product = Template.create({'name': 'Test product'})
        self.assertEqual(product.name, 'Test product')

    def test_compute_average_daily_consumption(self):
        product_template = self.env['product.template'].browse(
            self.test_product_template_id)
        product_template.calculation_range = 14  # trigger compute
        computed_value = product_template.average_consumption
        expected_value = 4.08
        self.assertEqual(computed_value, expected_value, 7)

    def test_compute_total_consumption(self):
        product_template = self.env['product.template'].browse(
            self.test_product_template_id)
        product_template.calculation_range = 14  # trigger compute
        computed_value = product_template.total_consumption
        expected_value = 57.11
        self.assertEqual(computed_value, expected_value)
