# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import Form, TransactionCase


class TestCPO(TransactionCase):
    def setUp(self):
        super().setUp()

        self.supplier = self.browse_ref("base.res_partner_1")
        self.pproduct1 = self.browse_ref("product.product_product_25")
        self.ptemplate1 = self.pproduct1.product_tmpl_id
        self.pproduct2 = self.browse_ref("product.product_delivery_02")
        self.ptemplate2 = self.pproduct2.product_tmpl_id

    def test_generate_pog(self):
        supplierinfo_obj = self.env["product.supplierinfo"]
        supplierinfo = supplierinfo_obj.search(
            [
                ("name", "=", self.supplier.id),
                ("product_tmpl_id", "=", self.ptemplate1.id),
            ]
        )
        supplierinfo2 = supplierinfo_obj.search(
            [
                ("name", "=", self.supplier.id),
                ("product_tmpl_id", "=", self.ptemplate2.id),
            ]
        )

        pog_obj = self.env["purchase.order.generator"]
        pog_action = pog_obj.with_context(
            active_ids=[self.ptemplate1.id]
        ).test_generate_pog()
        pog = pog_obj.browse(pog_action["res_id"])
        pogl = pog.pog_line_ids  # expect one line

        self.assertEquals(pog.supplier_id, self.supplier)
        self.assertEquals(pogl.product_template_id, self.ptemplate1)
        self.assertEquals(pogl.product_price, supplierinfo.price)
        self.assertEquals(pogl.purchase_quantity, supplierinfo.min_qty)

        # testing triggers
        expected_subtotal = supplierinfo.price * supplierinfo.min_qty
        self.assertEquals(pogl.subtotal, expected_subtotal)

        pogl.purchase_quantity = 4
        expected_subtotal = supplierinfo.price * 4
        self.assertEquals(pogl.subtotal, expected_subtotal)

        pog_form = Form(pog)
        with pog_form.pog_line_ids.edit(index=0) as line_form:
            line_form.product_template_id = self.ptemplate2
            self.assertEquals(line_form.product_template_id, self.ptemplate2)
        pog = pog_form.save()
        pogl = pog.pog_line_ids

        expected_subtotal = supplierinfo2.price * supplierinfo2.min_qty
        self.assertEquals(pogl.product_price, supplierinfo2.price)
        self.assertEquals(pogl.purchase_quantity, supplierinfo2.min_qty)
        self.assertEquals(pogl.subtotal, expected_subtotal)

    def test_generate_po(self):
        cpo_obj = self.env["purchase.order.generator"]
        cpo_action = cpo_obj.with_context(
            active_ids=[self.ptemplate1.id, self.ptemplate2.id]
        ).test_generate_pog()
        cpo = cpo_obj.browse(cpo_action["res_id"])
        po_action = cpo.create_purchase_order()
        po = self.env["purchase.order"].browse(po_action["res_id"])

        self.assertEquals(cpo.supplier_id, po.partner_id)
        self.assertEquals(len(cpo.pog_line_ids), len(po.order_line))
        lines = zip(
            cpo.pog_line_ids.sorted(lambda l: l.product_template_id),
            po.order_line.sorted(lambda l: l.product_id.product_tmpl_id),
        )
        for cpol, pol in lines:
            self.assertEquals(
                cpol.product_template_id, pol.product_id.product_tmpl_id
            )
            self.assertEquals(cpol.purchase_quantity, pol.product_qty)
