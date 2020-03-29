# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.product1 = self.browse_ref(
            "point_of_sale.whiteboard_pen"
        ).product_tmpl_id

    def test_compute_stock_coverage(self):
        self.product1._compute_stock_coverage()
        print("***")
        print(self.product1.range_sales)
        print(self.product1.daily_sales)
        print(self.product1.stock_coverage)
        print("***")
