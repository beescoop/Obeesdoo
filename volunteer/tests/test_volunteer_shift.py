# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from psycopg2.errors import CheckViolation

from odoo import Command
from odoo.exceptions import AccessError, ValidationError

from .test_volunteer_common import TestVolunteerCommon


class TestVolunteerShift(TestVolunteerCommon):
    def setUp(self):
        super().setUp()

        # Create shifts
        self.shift_utc_plus_1 = self.Shift.create(
            {
                "name": "LondonShift",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2027, 6, 6, 22, 59, 59),
                "end_time": datetime(2027, 6, 6, 23, 0, 1),
                "tz": "Europe/London",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        self.shift_utc_plus_2 = self.Shift.create(
            {
                "name": "Test",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2027, 6, 6, 22, 0, 1),
                "end_time": datetime(2027, 6, 7, 0, 0, 1),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )

    def test_compute_volunteer_ids(self):
        """Test that the volunteer_ids are correctly computed"""
        # There is one participation `confirmed` already defined in setUp()
        self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
        self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "canceled",
            }
        )
        self.assertEqual(
            self.shift_max_2.volunteer_ids,
            self.volunteer_confirmed | self.volunteer_confirmed2,
        )

    def test_is_one_day(self):
        """Test if a shift is one day or not"""
        shift_utc = self.Shift.create(
            {
                "name": "Test",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2027, 6, 6, 23, 59, 58),
                "end_time": datetime(2027, 6, 6, 23, 59, 59),
                "tz": "UTC",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )
        self.assertTrue(shift_utc.is_one_day)
        shift_utc = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime(2027, 6, 6, 23, 59, 59),
                "end_time": datetime(2027, 6, 7, 0, 0, 1),
                "tz": "UTC",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )
        self.assertFalse(shift_utc.is_one_day)

    def test_compute_time_located(self):
        """Test that the start_time_located and end_time_located
        are correctly computed with specific timezone"""
        # shift created with timezone Europe/London, UTC+1 summer time
        # UTC start_time = 2027-06-06 22:59:59
        # expected start_time_located = 2027-06-06 23:59:59
        # UTC end_time = 2027-06-06 23:00:01
        # expected end_time_located = 2027-06-07 00:00:01
        self.assertFalse(self.shift_utc_plus_1.is_one_day)
        # Shift created with timezone Europe/Brussels, UTC+2 summer time
        # UTC start_time = 2027-06-06 22:00:01
        # expected start_time_located = 2027-06-07 00:00:01
        # UTC end_time = 2027-06-07 00:00:01
        # expected end_time_located = 2027-06-07 02:00:01
        self.assertTrue(self.shift_utc_plus_2.is_one_day)

    def test_reduce_max_volunteer_equals_zero(self):
        """Test that it is not possible to reduce max_volunteer_nb to 0"""
        with self.assertRaises(CheckViolation):
            self.shift_utc_plus_2.write(
                {
                    "max_volunteer_nb": 0,
                }
            )

    def test_reduce_max_volunteer_under_confirmed_participation(self):
        """Test that it is not possible to reduce max_volunteer_nb
        under the number of confirmed participation"""
        # There is one confirmed participation defined in setUp()
        self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.shift_max_2.write(
                {
                    "max_volunteer_nb": 1,
                }
            )

    def test_compute_remaining_slots(self):
        """Test that the remaining slots are correctly computed"""
        # 1 participation confirmed, max_volunteer_nb = 2
        self.assertEqual(self.shift_max_2.remaining_slots, 1)

    def test_compute_remaining_slots_with_canceled_participation(self):
        """Test that the remaining slots are correctly computed
        when there is a canceled participation"""
        # There is one confirmed participation already defined in setUp()
        self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "canceled",
            }
        )
        self.assertEqual(self.shift_max_2.remaining_slots, 1)

    def test_volunteer_cannot_confirm_twice_for_same_shift(self):
        """Test that it is not possible to create multiple participation
        for the same volunteer"""
        with self.assertRaises(ValidationError):
            self.shift_max_2.write(
                {
                    "volunteer_participation_ids": [
                        Command.create({"volunteer_id": self.volunteer_confirmed.id}),
                    ]
                }
            )

    def test_cancel_shift_restrict_to_admin(self):
        """Test that only admin can cancel a shift"""
        with self.assertRaises(AccessError):
            self.shift_max_2.with_user(self.user_user).write(
                {
                    "stage_id": self.stage_canceled.id,
                }
            )
        with self.assertRaises(AccessError):
            self.shift_max_2.with_user(self.user_manager).write(
                {
                    "stage_id": self.stage_canceled.id,
                }
            )
        self.shift_max_2.with_user(self.user_admin).write(
            {
                "stage_id": self.stage_canceled.id,
            }
        )

    def test_cancel_all_participation_when_shift_is_canceled(self):
        """Test that all participation are canceled when the shift is canceled
        and do not overwrite cancellation_date on participation already canceled"""
        # There is one confirmed participation already defined in setUp()
        participation_canceled = self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "canceled",
            }
        )
        initial_cancellation_date = participation_canceled.cancellation_date
        participation_confirmed_2 = self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
        self.shift_max_2.with_user(self.user_admin).write(
            {
                "stage_id": self.stage_canceled.id,
            }
        )
        # Check that all participations are canceled
        # participation_confirmed is the one created in setUp()
        self.assertEqual(self.participation_confirmed.registration_state, "canceled")
        self.assertEqual(participation_confirmed_2.registration_state, "canceled")
        self.assertEqual(participation_canceled.registration_state, "canceled")
        # Check that the existing cancellation_date is not overwritten
        self.assertEqual(
            participation_canceled.registration_date, initial_cancellation_date
        )
