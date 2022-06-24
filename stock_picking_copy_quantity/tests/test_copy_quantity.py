# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCopyQuantity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.browse_ref("base.res_partner_2")
        self.picking_type_out = self.browse_ref("stock.picking_type_out")
        self.supplier_location = self.browse_ref("stock.stock_location_suppliers")
        self.stock_location = self.browse_ref("stock.stock_location_stock")
        self.product_a = self.env["product.product"].create({"name": "Product A"})
        self.product_b = self.env["product.product"].create({"name": "Product B"})

    def test_move_line_quantities_are_copied(self):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_a = self.env["stock.move"].create(
            {
                "name": self.product_a.name,
                "product_id": self.product_a.id,
                "product_uom_qty": 1,
                "product_uom": self.product_a.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move_b = self.env["stock.move"].create(
            {
                "name": self.product_b.name,
                "product_id": self.product_b.id,
                "product_uom_qty": 2,
                "product_uom": self.product_b.uom_id.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )

        picking.action_confirm()
        picking.copy_qty()
        self.assertEquals(move_a.move_line_ids.qty_done, 1)
        self.assertEquals(move_b.move_line_ids.qty_done, 2)
