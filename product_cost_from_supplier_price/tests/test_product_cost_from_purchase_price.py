# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import Command
from odoo.tests.common import TransactionCase


class ProductCostFromPurchasePriceCase(TransactionCase):
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

    def test_compute_product_cost_add_new_main_supplier(self):
        product = self.env.ref("product.product_product_10")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 120.5)
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.date_start = "2025-05-14"
        product.seller_ids = [
            Command.create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "price": 42,
                    "date_start": "2025-05-16",
                }
            )
        ]
        # the cost must be updated to the price of the new main supplier
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_add_new_non_main_supplier(self):
        product = self.env.ref("product.product_product_10")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 120.5)
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        self.assertEqual(product.standard_price, 42)
        product.seller_ids = [
            Command.create(
                {
                    "partner_id": self.env.ref("base.res_partner_1").id,
                    "price": 5,
                }
            )
        ]
        # the cost must not have changed
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_remove_main_supplier(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        main_supplier = product.main_supplierinfo_id
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertIn(supplierinfo_4.id, product.seller_ids.ids)
        self.assertNotEqual(supplierinfo_4, main_supplier)
        supplierinfo_4.price = 42
        # the cost must not have changed
        self.assertEqual(product.standard_price, 13)
        # remove main supplier
        product.seller_ids = [Command.delete(main_supplier.id)]
        # the other supplier should become the main supplier
        self.assertEqual(product.main_supplierinfo_id, supplierinfo_4)
        # the cost must be updated
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_remove_non_main_supplier(self):
        product = self.env.ref("product.product_product_7")
        self.assertEqual(product.standard_price, 14)
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        self.assertEqual(product.standard_price, 13)
        # reset the price to its original value
        product.standard_price = 14
        main_supplier = product.main_supplierinfo_id
        supplierinfo_4 = self.env.ref("product.product_supplierinfo_4")
        self.assertIn(supplierinfo_4.id, product.seller_ids.ids)
        self.assertNotEqual(supplierinfo_4, main_supplier)
        supplierinfo_4.price = 42
        # remove the non-main supplier
        product.seller_ids = [Command.delete(supplierinfo_4.id)]
        # the cost must not have changed
        self.assertEqual(product.standard_price, 14)

    def test_compute_product_cost_remove_all_suppliers(self):
        product = self.env.ref("product.product_product_10")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        supplierinfo = self.env.ref("product.product_supplierinfo_7")
        supplierinfo.price = 42
        product.seller_ids = [Command.clear()]
        # the cost must not have changed
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

    def test_compute_product_cost_on_product_creation(self):
        category = self.env.ref("product.product_category_5")
        category.property_cost_method = "standard_from_main_supplier_price"
        product = self.env["product.template"].create(
            {
                "name": "test product",
                "categ_id": category.id,
                "standard_price": 5,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": self.env.ref("base.res_partner_1").id,
                            "price": 42,
                        }
                    )
                ],
            }
        )
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_on_product_creation_only_if_supplier(self):
        category = self.env.ref("product.product_category_5")
        category.property_cost_method = "standard_from_main_supplier_price"
        product = self.env["product.template"].create(
            {
                "name": "test product",
                "categ_id": category.id,
                "standard_price": 42,
            }
        )
        self.assertEqual(product.standard_price, 42)

    def test_compute_product_cost_with_supplier_taxes(self):
        # this has include_base_amount set to False, so it will not affect the
        # computation of the next taxes.
        tax_10_included = self.env["account.tax"].create(
            {
                "name": "10% included",
                "amount_type": "percent",
                "amount": 10,
                "price_include": True,
                "include_base_amount": False,
                "sequence": 1,
            }
        )
        # this has include_base_amount set to True, so it will affect the
        # computation of the next taxes.
        tax_20_included = self.env["account.tax"].create(
            {
                "name": "20% included",
                "amount_type": "percent",
                "amount": 20,
                "price_include": True,
                "include_base_amount": True,
                "sequence": 2,
            }
        )
        # this is not included in the price, so it should be ignored.
        tax_30_excluded = self.env["account.tax"].create(
            {
                "name": "30% excluded",
                "amount_type": "percent",
                "amount": 30,
                "price_include": False,
                "sequence": 3,
            }
        )
        # this has include_base_amount set to True, so it will not affect the
        # computation of the next taxes.
        tax_40_included = self.env["account.tax"].create(
            {
                "name": "40% included",
                "amount_type": "percent",
                "amount": 40,
                "price_include": True,
                "include_base_amount": False,
                "sequence": 4,
            }
        )
        # this has include_base_amount set to False, so it will affect the
        # computation of the next taxes.
        tax_50_included = self.env["account.tax"].create(
            {
                "name": "50% included",
                "amount_type": "percent",
                "amount": 50,
                "price_include": True,
                "include_base_amount": True,
                "sequence": 5,
            }
        )
        # this has include_base_amount set to True, so it will affect the
        # computation of the next taxes, but because it is the last one, this
        # has no effect.
        tax_60_included = self.env["account.tax"].create(
            {
                "name": "60% included",
                "amount_type": "percent",
                "amount": 60,
                "price_include": True,
                "include_base_amount": True,
                "sequence": 6,
            }
        )
        product = self.env.ref("product.product_product_16")
        supplierinfo = self.env.ref("product.product_supplierinfo_10")
        product.categ_id.property_cost_method = "standard_from_main_supplier_price"
        # 100 * (0.1 + (1 + 0.2) * (0.4 + (1 + 0.5) * (1 + 0.6))) == 346
        supplierinfo.price = 346
        product.supplier_taxes_id = [
            Command.set(
                [
                    tax_10_included.id,
                    tax_20_included.id,
                    tax_30_excluded.id,
                    tax_40_included.id,
                    tax_50_included.id,
                    tax_60_included.id,
                ]
            )
        ]
        self.assertEqual(product.standard_price, 100)
