# Copyright 2021 Coop IT Easy SCRL fs
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import datetime

from odoo.tests import TransactionCase


class TestMainSeller(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product1 = self.env.ref("product.product_delivery_01")
        self.product2 = self.env.ref("product.product_delivery_02")
        self.product3 = self.env.ref("product.product_product_6")
        self.product1_main_supplierinfo_id = self.product1.seller_ids[0]
        self.product2_main_supplierinfo_id = self.product2.seller_ids[-1]

        # Set the first supplierinfo as the most recent one
        for index, sup in enumerate(self.product1.seller_ids):
            sup.date_start = datetime.date.today() - datetime.timedelta(weeks=index)
        # Set the last supplierinfo as the most recent one
        for index, sup in enumerate(self.product2.seller_ids):
            sup.date_start = datetime.date.today() + datetime.timedelta(weeks=index)
        # Remove all supplierinfo
        self.product3.seller_ids = False

    def test_get_main_suppplierinfo(self):
        """
        Check that the main supplierinfo is the most recent one.
        """
        self.assertEqual(
            self.product1.product_tmpl_id._get_main_supplier_info(),
            self.product1_main_supplierinfo_id,
        )
        self.assertEqual(
            self.product2.product_tmpl_id._get_main_supplier_info(),
            self.product2_main_supplierinfo_id,
        )
        self.assertFalse(self.product3.product_tmpl_id._get_main_supplier_info())
        self.assertFalse(self.product3.product_tmpl_id._get_main_supplier_info().price)
