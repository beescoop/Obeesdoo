# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.tests.common import TransactionCase


class ProductCostFromPurchasePriceCase(TransactionCase):
    @classmethod
    def setupClass(cls):
        pass

    def test_compute_product_cost_one_supplier(self):
        product = self.env.ref("product.product_product_10")
        self.assertEqual(product.standard_price, 120.5)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_category_cost_method_change(self):
        product = self.env.ref("product.product_product_10")
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        self.assertEqual(product.standard_price, 120.5)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 42)

    def test_dont_compute_with_wrong_cost_method(self):
        product = self.env.ref("product.product_product_10")
        self.assertEqual(product.standard_price, 120.5)
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        # the category cost method is "standard", not
        # "standard_from_main_supplier_price", so the cost must not have
        # changed
        self.assertEqual(product.standard_price, 120.5)

    def test_compute_product_cost_two_suppliers_no_start_date(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        # reset the price to its original value
        product.standard_price = 14
        main_supplier = product.main_supplierinfo_id
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertNotEqual(supplierinfo_4, main_supplier)
        supplierinfo_4.price = 42
        # the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_3 = self.env.ref("product.product_supplierinfo_3")
        # without a start date on any, the main supplier is the 1st one
        self.assertEqual(supplierinfo_3, main_supplier)
        supplierinfo_3.price = 42
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_two_suppliers_change_main_to_other(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        # reset the price to its original value
        product.standard_price = 14
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        supplierinfo_4.date_start = "2025-05-16"
        # this is still not the main supplier
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        # the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_3 = self.env.ref("product.product_supplierinfo_3")
        # without a start date, the main supplier is still this one
        self.assertEqual(supplierinfo_3, product.main_supplierinfo_id)
        supplierinfo_3.date_start = "2025-05-14"
        # with an earlier start date, the main supplier is now the other one
        self.assertEqual(supplierinfo_4, product.main_supplierinfo_id)
        # this is not the main supplier anymore, thus the cost should be set
        # to the one of the new main supplier
        self.assertEqual(product.standard_price, 14.4)

    def test_compute_product_cost_two_suppliers_change_main_to_self(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        # reset the price to its original value
        product.standard_price = 14
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        supplierinfo_4.date_start = "2025-05-12"
        # this is still not the main supplier
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        # the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_3 = self.env.ref("product.product_supplierinfo_3")
        # without a start date, the main supplier is still this one
        self.assertEqual(supplierinfo_3, product.main_supplierinfo_id)
        supplierinfo_3.date_start = "2025-05-14"
        # with a later start date, the main supplier is still this one
        self.assertEqual(supplierinfo_3, product.main_supplierinfo_id)
        # this is still the main supplier, so the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_4.date_start = "2025-05-16"
        # with an even later start date, this is now the main supplier
        self.assertEqual(supplierinfo_4, product.main_supplierinfo_id)
        # the cost must be updated
        self.assertEqual(product.standard_price, 14.4)

    def test_compute_product_cost_two_suppliers_change_main_to_self_and_price(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        # reset the price to its original value
        product.standard_price = 14
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        supplierinfo_4.date_start = "2025-05-12"
        # this is still not the main supplier
        self.assertNotEqual(supplierinfo_4, product.main_supplierinfo_id)
        # the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_3 = self.env.ref("product.product_supplierinfo_3")
        # without a start date, the main supplier is still this one
        self.assertEqual(supplierinfo_3, product.main_supplierinfo_id)
        supplierinfo_3.date_start = "2025-05-14"
        # with a later start date, the main supplier is still this one
        self.assertEqual(supplierinfo_3, product.main_supplierinfo_id)
        # this is still the main supplier, so the cost must not have changed
        self.assertEqual(product.standard_price, 14)
        supplierinfo_4.write({"date_start": "2025-05-16", "price": 42})
        # with an even later start date, this is now the main supplier
        self.assertEqual(supplierinfo_4, product.main_supplierinfo_id)
        # the cost must be updated
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_multiple_variants(self):
        product = self.env.ref("product.product_product_11")
        self.assertEqual(product.standard_price, 0)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 0)
        supplierinfo = self.env.ref("product.product_supplierinfo_8")
        supplierinfo.price = 42
        # the cost must not be updated, as there are multiple variants
        self.assertEqual(product.standard_price, 0)

    def test_compute_product_cost_no_price_update(self):
        product = self.env.ref("product.product_product_10")
        self.assertEqual(product.standard_price, 120.5)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        self.assertEqual(product.standard_price, 42)
        # reset the price to its original value
        product.standard_price = 120.5
        supplierinfo.date_start = "2025-05-16"
        # the cost must not be updated, as the price hasn't changed
        self.assertEqual(product.standard_price, 120.5)

    def test_compute_product_cost_uom_conversion(self):
        product = self.env.ref("product.product_product_10")
        product.uom_po_id = self.env.ref("uom.product_uom_dozen")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42 * 12
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_uom_po_change(self):
        product = self.env.ref("product.product_product_10")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42 * 12
        self.assertEqual(product.standard_price, 42 * 12)
        product.uom_po_id = self.env.ref("uom.product_uom_dozen")
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_uom_change(self):
        product = self.env.ref("product.product_product_16")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_10")
        supplierinfo.price = 42
        self.assertEqual(product.standard_price, 42)
        product.uom_id = self.env.ref("uom.product_uom_dozen")
        self.assertEqual(product.standard_price, 42 * 12)
