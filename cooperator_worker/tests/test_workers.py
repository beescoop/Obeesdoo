# Copyright 2020 Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .common import TestWorkerBase


class TestWorkers(TestWorkerBase):
    def test_is_worker_share_x(self):
        """
        Test that a cooperator is a worker based on his share type.
        """
        self.assertEqual(self.cooperator_x.is_worker, True)

    def test_is_worker_share_y(self):
        """
        Test that a cooperator is a worker based on his share type.
        """
        self.assertEqual(self.cooperator_y.is_worker, False)

    def test_search_worker(self):
        """
        Test that the search function returns worker based on the
        computed 'is_worker' field.
        """
        workers = self.env["res.partner"].search([("is_worker", "=", True)])
        self.assertIn(self.cooperator_x, workers)
        self.assertNotIn(self.cooperator_y, workers)

        not_workers = self.env["res.partner"].search([("is_worker", "=", False)])
        self.assertNotIn(self.cooperator_x, not_workers)
        self.assertIn(self.cooperator_y, not_workers)

    def test_compute_can_shop_share_x(self):
        """
        Test that a cooperator can shop based on his share type.
        """
        # using self.env.ref("shift.res_partner_worker_1_demo")
        # does not work because the is_worker field is overriden by
        # cooperator_worker's `_compute_is_worker`

        cooperative_status = self.env["cooperative.status"].create(
            {
                "cooperator_id": self.cooperator_x.id,
                "super": True,
                "working_mode": "regular",
                "sr": 2,
            }
        )
        self.assertEqual(self.cooperator_x.can_shop, True)

        # Now unsubscribe the coop
        cooperative_status.status = "resigning"
        self.assertEqual(cooperative_status.can_shop, False)
        self.assertEqual(self.cooperator_x.can_shop, False)
