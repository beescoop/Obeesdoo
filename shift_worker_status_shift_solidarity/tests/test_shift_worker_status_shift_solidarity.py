# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from freezegun import freeze_time

from odoo.addons.shift_solidarity.tests.test_shift_solidarity_common import (
    TestShiftSolidarityCommon,
)


class TestShiftWorkerStatusSolidarity(TestShiftSolidarityCommon):
    def test_irregular_counter_solidarity_request(self):
        """Test that the personal counter updates when requesting
        a solidarity shift or cancelling a request
        """
        self.worker_irregular_1.cooperative_status_ids.sr = 0

        self.shift1_d2_w1_t1.worker_id = self.worker_irregular_1

        request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_irregular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
                "state": "validated",
            }
        )
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 1)

        request.state = "cancelled"
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 0)

    def test_counter_solidarity_offer(self):
        """Verify that the personal counter of an irregular worker is not
        incremented when doing a solidarity shift
        """
        self.worker_irregular_1.cooperative_status_ids.sr = 0
        offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_irregular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
                "state": "validated",
            }
        )
        with freeze_time(self.future):
            offer.shift_id.state = "done"
        self.assertEqual(self.worker_irregular_1.cooperative_status_ids.sr, 0)
