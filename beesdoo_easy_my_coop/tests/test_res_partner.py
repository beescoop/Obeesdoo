# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
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
        coop1 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_1_demo"
        )
        coop1.write({"child_eater_ids": [(4, self.eater1.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 1)
        coop1.write({"child_eater_ids": [(4, self.eater2.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 2)
        coop1.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertEqual(len(coop1.child_eater_ids), 3)
        with self.assertRaises(ValidationError) as econtext:
            coop1.write({"child_eater_ids": [(4, self.eater4.id)]})
        self.assertIn("can only set", str(econtext.exception))

    def test_max_eater_assignment_share_b(self):
        """
        Test adding eater to a cooperator and raise when max is
        reached.
        """
        coop2 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_2_demo"
        )
        coop2.write({"child_eater_ids": [(4, self.eater1.id)]})
        self.assertEqual(len(coop2.child_eater_ids), 1)
        coop2.write({"child_eater_ids": [(4, self.eater2.id)]})
        self.assertEqual(len(coop2.child_eater_ids), 2)
        with self.assertRaises(ValidationError) as econtext:
            coop2.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertIn("can only set", str(econtext.exception))

    def test_unlimited_eater_assignment_share_c(self):
        """
        Test that share_c can have an unlimited number of eater.
        """
        coop3 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_3_demo"
        )
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
        coop3 = self.env.ref(
            "beesdoo_base.res_partner_cooperator_3_demo"
        )
        with self.assertRaises(ValidationError) as econtext:
            coop3.write({"child_eater_ids": [(4, self.eater3.id)]})
        self.assertIn("can only set", str(econtext.exception))
