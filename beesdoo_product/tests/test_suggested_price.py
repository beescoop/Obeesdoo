# Copyright 2021 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests import TransactionCase
from odoo.tools import float_compare


class TestSuggestedPrice(TransactionCase):
    def setUp(self):
        super(TestSuggestedPrice, self).setUp()

        (
            self.env["ir.config_parameter"]
            .sudo()
            .set_param(
                "beesdoo_product.suggested_price_reference", "sale_price"
            )
        )
        self.account_type_ass = self.env.ref(
            "account.data_account_type_current_assets"
        )
        self.a_debit_vat = self.env["account.account"].create(
            {
                "code": "debvat_acc",
                "name": "debit vat account",
                "user_type_id": self.account_type_ass.id,
                "reconcile": False,
            }
        )
        self.sale_tax_2_5 = self.env["account.tax"].create(
            {
                "name": "Tax 2.5 Incl.",
                "amount": 2.5,
                "amount_type": "percent",
                "type_tax_use": "sale",
                "account_id": self.a_debit_vat.id,
                "price_include": True,
            }
        )
        self.unit_uom = self.env.ref("uom.product_uom_unit")
        self.kg_uom = self.env.ref("uom.product_uom_kgm")
        self.product_category = self.env.ref("product.product_category_all")
        self.product_category.should_round_suggested_price = True
        self.supplier = self.env.ref("base.res_partner_1")
        self.supplier.profit_margin = 25

    def test_suggested_price_same_unit(self):
        product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "taxes_id": [(4, self.sale_tax_2_5.id)],
                "uom_id": self.unit_uom.id,
                "uom_po_id": self.unit_uom.id,
                "categ_id": self.product_category.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "price": 14.77,
                "product_tmpl_id": product.product_tmpl_id.id,
            }
        )
        self.assertEqual(
            float_compare(product.suggested_price, 20.20, precision_digits=3),
            0,
        )

    def test_suggested_price_unit_conversion(self):
        sale_unit = self.env["uom.uom"].create(
            {
                "category_id": self.env.ref("uom.product_uom_categ_kgm").id,
                "name": "2.5 kg",
                "factor": 2.5,
                "rounding": 0.001,
                "uom_type": "bigger",
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Test Product",
                "taxes_id": [(4, self.sale_tax_2_5.id)],
                "uom_id": self.kg_uom.id,
                "uom_po_id": sale_unit.id,
                "categ_id": self.product_category.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "name": self.supplier.id,
                "price": 1.55,
                "product_tmpl_id": product.product_tmpl_id.id,
            }
        )
        self.assertEqual(
            float_compare(product.suggested_price, 5.3, precision_digits=3), 0,
        )
