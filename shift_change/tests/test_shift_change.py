# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime, timedelta

from psycopg2.errors import IntegrityError

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestShiftChange(TransactionCase):
    def setUp(self):
        super().setUp()

        # Force all operations to run as admin
        self.env = self.env(user=self.env.ref("base.user_admin"))

        self.shift_model = self.env["shift.shift"]
        self.shift_template_model = self.env["shift.template"]
        self.shift_change_model = self.env["shift.change"]

        self.now = datetime.now()

        self.worker_regular_1 = self.env.ref("shift.res_partner_worker_1_demo")
        self.worker_regular_2 = self.env.ref("shift.res_partner_worker_3_demo")
        self.worker_irregular_1 = self.env.ref("shift.res_partner_worker_2_demo")

        self.task_template_1 = self.env.ref("shift_change.task_template_1_demo")
        self.task_template_2 = self.env.ref("shift_change.task_template_2_demo")
        self.task_template_3 = self.env.ref("shift_change.task_template_3_demo")

        self.shift_1 = self.shift_model.create(
            {
                "name": "shift_1",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_1.id,
            }
        )
        self.shift_2 = self.shift_model.create(
            {
                "name": "shift_2",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=2),
                "end_time": self.now + timedelta(days=2),
                "is_regular": True,
                "worker_id": self.worker_regular_2.id,
            }
        )
        self.shift_3 = self.shift_model.create(
            {
                "name": "shift_3",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now + timedelta(days=4),
                "worker_id": False,
            }
        )
        self.shift_4 = self.shift_model.create(
            {
                "name": "shift_4",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now - timedelta(days=4),
                "end_time": self.now,
                "worker_id": False,
            }
        )
        self.shift_5 = self.shift_model.create(
            {
                "name": "shift_5",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now,
                "worker_id": False,
            }
        )
        self.shift_6 = self.shift_model.create(
            {
                "name": "shift_6",
                "task_template_id": self.task_template_2.id,
                "start_time": self.now + timedelta(hours=1),
                "end_time": self.now,
                "worker_id": False,
            }
        )

        # Set context to avoid shift generation in the past
        self.env.context = dict(self.env.context, visualize_date=date.today())

        # Set maximum change shift for testing
        self.env["ir.config_parameter"].set_param(
            "shift_change.same_shift_change_max", 1
        )

    def test_get_available_new_shift_ids(self):
        """Test available new shift"""
        available_shifts = self.shift_change_model._get_available_new_shift_ids(
            self.worker_regular_1
        )
        expected_shifts = self.shift_3 | self.shift_5 | self.shift_6
        self.assertEqual(
            available_shifts,
            expected_shifts,
        )
        self.shift_1.write({"worker_id": False, "is_regular": False})
        available_shifts = self.shift_change_model._get_available_new_shift_ids(
            self.worker_regular_1
        )
        expected_shifts = self.shift_1 | self.shift_3 | self.shift_5 | self.shift_6
        self.assertEqual(
            available_shifts,
            expected_shifts,
        )

    def test_shift_change(self):
        """Test change a shift"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        self.shift_change_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "old_shift_id": self.shift_1.id,
                "new_shift_id": self.shift_3.id,
            }
        )
        self.assertFalse(self.shift_1.worker_id)
        self.assertEqual(self.shift_3.worker_id, self.worker_regular_1)

    def test_shift_change_max(self):
        """Test change a shift several times"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        self.assertFalse(self.shift_5.worker_id)
        self.shift_change_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "old_shift_id": self.shift_1.id,
                "new_shift_id": self.shift_3.id,
            }
        )
        self.assertFalse(self.shift_1.worker_id)
        self.assertEqual(self.shift_3.worker_id, self.worker_regular_1)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_3.id,
                    "new_shift_id": self.shift_5.id,
                }
            )

    def test_shift_change_not_empty(self):
        """Test changing a shift to a non empty shift"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertEqual(self.shift_2.worker_id, self.worker_regular_2)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_1.id,
                    "new_shift_id": self.shift_2.id,
                }
            )

    def test_shift_change_in_past(self):
        """Test changing for a shift in the past"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_4.worker_id)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_1.id,
                    "new_shift_id": self.shift_4.id,
                }
            )

    def test_shift_change_wrong_worker(self):
        """Test creating a change with worker that don't match the shift
        worker
        """
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_2.id,
                    "old_shift_id": self.shift_1.id,
                    "new_shift_id": self.shift_4.id,
                }
            )

    def test_shift_change_missing_required_fields(self):
        """Test creating a shift with missing fields"""
        with self.assertRaises(IntegrityError):
            with mute_logger("odoo.sql_db"):
                self.shift_change_model.create(
                    {
                        "worker_id": self.worker_regular_1.id,
                    }
                )

    def test_shift_change_writing(self):
        """Test that writing to a shift fails"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        shift_change = self.shift_change_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "old_shift_id": self.shift_1.id,
                "new_shift_id": self.shift_3.id,
            }
        )
        with self.assertRaises(AccessError):
            shift_change.write(
                {
                    "new_shift_id": self.shift_4.id,
                }
            )

    def test_shift_change_to_close(self):
        """Test changing to a shift to close"""
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_6.worker_id)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_1.id,
                    "new_shift_id": self.shift_6.id,
                }
            )

    def test_shift_origin_empty(self):
        """Test that fails if old_shift is empty"""
        self.assertFalse(self.shift_4.worker_id)
        self.assertFalse(self.shift_3.worker_id)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_4.id,
                    "new_shift_id": self.shift_3.id,
                }
            )

    def test_new_shift_not_available(self):
        """Test that fails if worker has already subscribed to a sibling
        of new_shift"""
        # create siblings
        self.shift_7 = self.shift_model.create(
            {
                "name": "shift_7",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now + timedelta(days=4),
                "is_regular": True,
                "worker_id": self.worker_regular_1.id,
            }
        )
        self.shift_7_bis = self.shift_model.create(
            {
                "name": "shift_7_bis",
                "task_template_id": self.task_template_1.id,
                "start_time": self.now + timedelta(days=4),
                "end_time": self.now + timedelta(days=4),
                "worker_id": False,
            }
        )
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_7_bis.worker_id)
        with self.assertRaises(ValidationError):
            self.shift_change_model.create(
                {
                    "worker_id": self.worker_regular_1.id,
                    "old_shift_id": self.shift_1.id,
                    "new_shift_id": self.shift_7_bis.id,
                }
            )

    def test_shift_change_loop(self):
        """Test change a shift"""
        # Set maximum change shift for testing
        self.env["ir.config_parameter"].set_param(
            "shift_change.same_shift_change_max", 3
        )
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
        self.shift_change_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "old_shift_id": self.shift_1.id,
                "new_shift_id": self.shift_3.id,
            }
        )
        self.assertFalse(self.shift_1.worker_id)
        self.assertEqual(self.shift_3.worker_id, self.worker_regular_1)
        self.shift_change_model.create(
            {
                "worker_id": self.worker_regular_1.id,
                "old_shift_id": self.shift_3.id,
                "new_shift_id": self.shift_1.id,
            }
        )
        self.assertEqual(self.shift_1.worker_id, self.worker_regular_1)
        self.assertFalse(self.shift_3.worker_id)
