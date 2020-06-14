# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.eater1 = self.env.ref("beesdoo_base.eater1")
        self.eater2 = self.env.ref("beesdoo_base.eater2")
        self.eater3 = self.env.ref("beesdoo_base.eater3")
        self.eater4 = self.env.ref("beesdoo_base.eater4")

    def test_max_eater_assignment_share_a(self):
        """
        Test adding eater to a cooperator and raise when max is
        reached.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        coop1.write({"child_eater_ids": [(4, self.eater1.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 1)
        coop1.write({"child_eater_ids": [(4, self.eater2.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 2)
        coop1.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 3)
        with self.assertRaises(ValidationError) as econtext:
            coop1.write({"child_eater_ids": [(4, self.eater4.id)]})
        self.assertIn("can only set", str(econtext.exception))
        # Reset
        coop1.write({"child_eater_ids": [(5, None, None)]})
        self.assertEqual(len(coop1.child_eater_ids), 0)
        # Test by editing parent_eater_id
        self.eater1.write({"parent_eater_id": coop1.id})
        self.assertEqual(len(coop1.child_eater_ids), 1)
        self.eater2.write({"parent_eater_id": coop1.id})
        self.assertEqual(len(coop1.child_eater_ids), 2)
        self.eater3.write({"parent_eater_id": coop1.id})
        self.assertEqual(len(coop1.child_eater_ids), 3)
        with self.assertRaises(ValidationError) as econtext:
            self.eater4.write({"parent_eater_id": coop1.id})
        self.assertIn("can only set", str(econtext.exception))

    def test_max_eater_assignment_share_b(self):
        """
        Test adding eater to a cooperator and raise when max is
        reached.
        """
        coop2 = self.env.ref("beesdoo_base.res_partner_cooperator_2_demo")
        coop2.write({"child_eater_ids": [(4, self.eater1.id)]})
        self.assertEqual(len(coop2.child_eater_ids), 1)
        coop2.write({"child_eater_ids": [(4, self.eater2.id)]})
        self.assertEqual(len(coop2.child_eater_ids), 2)
        with self.assertRaises(ValidationError) as econtext:
            coop2.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertIn("can only set", str(econtext.exception))
        # Reset
        coop2.write({"child_eater_ids": [(5, None, None)]})
        self.assertEqual(len(coop2.child_eater_ids), 0)
        # Test by editing parent_eater_id
        self.eater1.write({"parent_eater_id": coop2.id})
        self.assertEqual(len(coop2.child_eater_ids), 1)
        self.eater2.write({"parent_eater_id": coop2.id})
        self.assertEqual(len(coop2.child_eater_ids), 2)
        with self.assertRaises(ValidationError) as econtext:
            self.eater3.write({"parent_eater_id": coop2.id})
        self.assertIn("can only set", str(econtext.exception))

    def test_unlimited_eater_assignment_share_c(self):
        """
        Test that share_c can have an unlimited number of eater.
        """
        coop3 = self.env.ref("beesdoo_base.res_partner_cooperator_3_demo")
        coop3.write({"child_eater_ids": [(4, self.eater1.id)]})
        self.assertEqual(len(coop3.child_eater_ids), 1)
        coop3.write({"child_eater_ids": [(4, self.eater2.id)]})
        self.assertEqual(len(coop3.child_eater_ids), 2)
        coop3.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertEqual(len(coop3.child_eater_ids), 3)
        coop3.write({"child_eater_ids": [(4, self.eater4.id)]})
        self.assertEqual(len(coop3.child_eater_ids), 4)

    def test_share_with_no_eater_assignment_allowed(self):
        """
        Test that share that doesn't allow eater assignment.
        """
        share_c = self.env.ref("beesdoo_easy_my_coop.share_c")
        share_c.max_nb_eater_allowed = 0
        coop3 = self.env.ref("beesdoo_base.res_partner_cooperator_3_demo")
        with self.assertRaises(ValidationError) as econtext:
            coop3.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertIn("can only set", str(econtext.exception))
        with self.assertRaises(ValidationError) as econtext:
            self.eater1.write({"parent_eater_id": coop3.id})
        self.assertIn("can only set", str(econtext.exception))

    def test_multiple_eater_assignement_share_a(self):
        """
        Test adding multiple eater in one write.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        coop1.write(
            {
                "child_eater_ids": [
                    (4, self.eater1.id),
                    (4, self.eater2.id),
                    (4, self.eater3.id),
                ]
            }
        )
        self.assertEqual(len(coop1.child_eater_ids), 3)

    def test_parent_assignement_to_eater(self):
        """
        Test adding a parent to multiple eater in one write from the eater.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        eaters = self.eater1
        eaters |= self.eater2
        eaters |= self.eater3
        eaters.write({"parent_eater_id": coop1.id})
        self.assertEqual(len(coop1.child_eater_ids), 3)

    def test_is_worker_share_a(self):
        """
        Test that a cooperator is a worker based on his share type.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        # Run computed field
        coop1._compute_is_worker()
        self.assertEqual(coop1.is_worker, True)

    def test_is_worker_share_b(self):
        """
        Test that a cooperator is a worker based on his share type.
        """
        coop2 = self.env.ref("beesdoo_base.res_partner_cooperator_2_demo")
        # Run computed field
        coop2._compute_is_worker()
        self.assertEqual(coop2.is_worker, False)

    def test_search_worker(self):
        """
        Test that the search function returns worker based on the
        'is_worker' field.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        coop2 = self.env.ref("beesdoo_base.res_partner_cooperator_2_demo")
        # Run computed field
        coop1._compute_is_worker()
        coop2._compute_is_worker()
        workers = self.env["res.partner"].search([("is_worker", "=", True)])
        self.assertIn(coop1, workers)
        self.assertNotIn(coop2, workers)
        workers = self.env["res.partner"].search([("is_worker", "=", False)])
        self.assertNotIn(coop1, workers)
        self.assertIn(coop2, workers)

    def test_compute_can_shop_share_a(self):
        """
        Test that a cooperator can shop based on his share type.
        """
        coop1 = self.env.ref("beesdoo_base.res_partner_cooperator_1_demo")
        # Run computed field
        coop1._compute_can_shop()
        self.assertEqual(coop1.can_shop, True)
        # Now unsubscribe the coop
        coop1.cooperative_status_ids.status = "resigning"
        self.assertEqual(coop1.cooperative_status_ids.can_shop, False)
        self.assertEqual(coop1.can_shop, False)

    def test_compute_can_shop_share_c(self):
        """
        Test that a cooperator can shop based on his share type.
        """
        coop3 = self.env.ref("beesdoo_base.res_partner_cooperator_3_demo")
        # Run computed field
        coop3._compute_can_shop()
        self.assertEqual(coop3.can_shop, False)
