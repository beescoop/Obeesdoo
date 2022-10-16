# Copyright 2020 Coop IT Easy SC (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from datetime import date

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError

from odoo.addons.cooperator_worker.tests.test_base import TestWorkerBase


class TestEaters(TestWorkerBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        partner_obj = cls.env["res.partner"]
        ptemplate_obj = cls.env["product.template"]

        cls.eater_1 = partner_obj.create(
            {"name": "Eater 1", "customer": True, "eater": "eater"}
        )
        cls.eater_2 = partner_obj.create(
            {"name": "Eater 2", "customer": True, "eater": "eater"}
        )
        cls.eater_3 = partner_obj.create(
            {"name": "Eater 3", "customer": True, "eater": "eater"}
        )
        cls.eater_4 = partner_obj.create(
            {"name": "Eater 4", "customer": True, "eater": "eater"}
        )

        cls.worker_share = ptemplate_obj.create(
            {
                "name": "Worker Share",
                "is_share": True,
                "eater": "worker_eater",
            }
        )
        cls.eater_share = ptemplate_obj.create(
            {
                "name": "Eater Share",
                "is_share": True,
                "eater": "eater",
            }
        )

    def test_max_eater_assignment_to_positive_integer(self):
        """
        Test adding eater to a cooperator and raise when max is
        reached.
        """
        self.share_x.max_nb_eater_allowed = 3
        self.cooperator_x.write(
            {
                "child_eater_ids": [
                    (6, 0, [self.eater_1.id, self.eater_2.id, self.eater_3.id])
                ]
            }
        )
        self.assertEqual(len(self.cooperator_x.child_eater_ids), 3)

        max_eater_error_msg = "You can only set 3 additional eaters per worker"
        with self.assertRaisesRegex(ValidationError, max_eater_error_msg):
            self.cooperator_x.write({"child_eater_ids": [(4, self.eater_4.id)]})

        # Reset
        self.cooperator_x.write({"child_eater_ids": [(5, None, None)]})
        self.assertEqual(len(self.cooperator_x.child_eater_ids), 0)
        # Test by editing parent_eater_id
        self.eater_1.parent_eater_id = self.cooperator_x.id
        self.eater_2.parent_eater_id = self.cooperator_x.id
        self.eater_3.parent_eater_id = self.cooperator_x.id
        self.assertEqual(len(self.cooperator_x.child_eater_ids), 3)

        with self.assertRaisesRegex(ValidationError, max_eater_error_msg):
            self.eater_4.write({"parent_eater_id": self.cooperator_x.id})

    def test_unlimited_eater_assignment(self):
        """
        Test that  can have an unlimited number of eater.
        """
        self.share_y.max_nb_eater_allowed = -1
        self.cooperator_y.write(
            {
                "child_eater_ids": [
                    (
                        6,
                        0,
                        [
                            self.eater_1.id,
                            self.eater_2.id,
                            self.eater_3.id,
                            self.eater_4.id,
                        ],
                    )
                ]
            }
        )
        self.assertEqual(len(self.cooperator_y.child_eater_ids), 4)

    def test_share_with_no_eater_assignment_allowed(self):
        """
        Test that share that doesn't allow eater assignment.
        """
        self.share_z.max_nb_eater_allowed = 0

        max_eater_error_msg = "You can only set 0 additional eaters per worker"
        with self.assertRaisesRegex(ValidationError, max_eater_error_msg):
            self.cooperator_z.write({"child_eater_ids": [(4, self.eater_1.id)]})

        with self.assertRaisesRegex(ValidationError, max_eater_error_msg):
            self.eater_1.write({"parent_eater_id": self.cooperator_z.id})

    def test_get_eater_vals_returns_share_zonfiguration(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Partner with birthdate set",
                "birthdate_date": date.today() - relativedelta(years=30),
            }
        )

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.worker_share
        )
        self.assertEqual(vals["eater"], "worker_eater")

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.eater_share
        )
        self.assertEqual(vals["eater"], "eater")

    def test_get_eater_vals_returns_worker_eater_for_unset_birthdate(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Partner without birthdate set",
            }
        )

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.worker_share
        )
        self.assertEqual(vals["eater"], "worker_eater")

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.eater_share
        )
        self.assertEqual(vals["eater"], "eater")

    def test_get_eater_vals_returns_eater_for_youngsters(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Young Partner",
                "birthdate_date": date.today() - relativedelta(years=15),
            }
        )

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.worker_share
        )
        self.assertEqual(vals["eater"], "eater")

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.eater_share
        )
        self.assertEqual(vals["eater"], "eater")

    def test_get_eater_vals_returns_eater_for_newborns(self):
        """
        Test that get_eater_vals() work correctly when the partner is 0 years
        old.
        """
        partner = self.env["res.partner"].create(
            {
                "name": "Newborn Partner",
                "birthdate_date": date.today() - relativedelta(days=180),
            }
        )

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.worker_share
        )
        self.assertEqual(vals["eater"], "eater")

        vals = self.env["subscription.request"].get_eater_vals(
            partner, self.eater_share
        )
        self.assertEqual(vals["eater"], "eater")
