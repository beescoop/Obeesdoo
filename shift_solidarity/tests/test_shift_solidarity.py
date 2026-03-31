# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError

from .test_shift_solidarity_common import TestShiftSolidarityCommon


class TestShiftSolidarity(TestShiftSolidarityCommon):
    def test_solidarity_offer_create_draft(self):
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
            }
        )
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)

    def test_solidarity_offer_create(self):
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
                "state": "validated",
            }
        )
        self.assertEqual(self.shift3_d4_nw_t2.worker_id, self.worker_regular_1)

    def test_solidarity_offer_write(self):
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
            }
        )
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        offer.state = "validated"
        self.assertEqual(self.shift3_d4_nw_t2.worker_id, self.worker_regular_1)

    def test_cancel_solidarity_offer(self):
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
                "state": "validated",
            }
        )
        self.assertEqual(self.shift3_d4_nw_t2.worker_id, self.worker_regular_1)
        offer.state = "cancelled"
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)

    def test_cancel_solidarity_offer_too_late(self):
        self.assertFalse(self.shift3_d4_nw_t2.worker_id)
        offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
                "state": "validated",
            }
        )
        self.assertEqual(self.shift3_d4_nw_t2.worker_id, self.worker_regular_1)
        # Change parameter for offer limit time
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_offer_hour_limit", 240
        )
        with self.assertRaises(UserError):
            offer.state = "cancelled"

    def test_solidarity_request_create_draft(self):
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)
        self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
                "reason": "This is a real reason.",
            }
        )
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)

    def test_solidarity_request_create(self):
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)
        self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
                "state": "validated",
            }
        )
        self.assertFalse(self.shift1_d2_w1_t1.worker_id)

    def test_solidarity_request_write(self):
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)
        request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
            }
        )
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)
        request.state = "validated"
        self.assertFalse(self.shift1_d2_w1_t1.worker_id)

    def test_cancel_solidarity_request(self):
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)
        request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
                "state": "validated",
            }
        )
        self.assertFalse(self.shift1_d2_w1_t1.worker_id)
        request.state = "cancelled"
        self.assertTrue(self.shift1_d2_w1_t1.worker_id)

    def test_solidarity_counter(self):
        self.assertEqual(self.env["res.company"].solidarity_counter(), 0)
        # create in draft state: should not impact the counter
        offer = self.shift_solidarity_offer_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift3_d4_nw_t2.id,
            }
        )
        self.assertEqual(self.env["res.company"].solidarity_counter(), 0)
        # validate offer: should not impact the counter
        offer.state = "validated"
        self.assertEqual(self.env["res.company"].solidarity_counter(), 0)
        with freeze_time(self.future):
            # validate shift: should impact the counter
            offer.shift_id.state = "done"
        self.assertEqual(self.env["res.company"].solidarity_counter(), 1)
        # create an request in draft state: should not impact the counter
        request = self.shift_solidarity_request_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "shift_id": self.shift1_d2_w1_t1.id,
            }
        )
        self.assertEqual(self.env["res.company"].solidarity_counter(), 1)
        request.state = "validated"
        self.assertEqual(self.env["res.company"].solidarity_counter(), 0)
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_counter_start_value", 10
        )
        self.assertEqual(self.env["res.company"].solidarity_counter(), 10)

    def test_solidarity_counter_limit(self):
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.solidarity_counter_limit", 0
        )
        self.assertEqual(self.env["res.company"].solidarity_counter(), 0)
        with self.assertRaises(ValidationError):
            self.shift_solidarity_request_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "shift_id": self.shift1_d2_w1_t1.id,
                    "state": "validated",
                }
            )

    def test_max_solidarity_request_number(self):
        self.env["ir.config_parameter"].set_param(
            "shift_solidarity.max_solidarity_requests_number", 0
        )
        with self.assertRaises(ValidationError):
            self.shift_solidarity_request_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "shift_id": self.shift1_d2_w1_t1.id,
                    "state": "validated",
                }
            )

    def test_offer_hour_limit(self):
        with self.assertRaises(ValidationError):
            self.shift_solidarity_offer_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "shift_id": self.shift6_h1_nw_t2.id,
                    "state": "validated",
                }
            )

    def test_request_hour_limit(self):
        with self.assertRaises(UserError):
            self.shift_solidarity_request_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "shift_id": self.shift7_h1_w1_t1.id,
                    "state": "validated",
                }
            )
