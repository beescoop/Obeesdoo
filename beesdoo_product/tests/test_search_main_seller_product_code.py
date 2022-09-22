# Copyright 2021 Coop IT Easy SCRL fs
#   Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import TransactionCase


class TestSearchMainSellerProductCode(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product1 = self.env.ref("product.product_delivery_01")
        self.product2 = self.env.ref("product.product_delivery_02")

        for index, sup in enumerate(self.product1.seller_ids):
            sup.product_code = "AAA%d" % index
        for index, sup in enumerate(self.product2.seller_ids):
            sup.product_code = "BBB%d" % index

    def test_search_product_by_main_seller_product_code(self):
        """
        Test searching a product giving the product_code of it's
        main_seller_id
        """
        products = self.env["product.product"].search(
            [
                (
                    "main_seller_id_product_code",
                    "=",
                    self.product1.top_supplierinfo_id.product_code,
                )
            ]
        )
        self.assertEqual(products, self.product1)
        products = self.env["product.product"].search(
            [
                (
                    "main_seller_id_product_code",
                    "=",
                    self.product2.top_supplierinfo_id.product_code,
                )
            ]
        )
        self.assertEqual(products, self.product2)
