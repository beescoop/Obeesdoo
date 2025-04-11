# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from psycopg2.errors import CheckViolation

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import datetime

from .test_volunteer_common import TestVolunteerCommon


class TestShift(TestVolunteerCommon):
    def setUp(self):
        super().setUp()

        # Create shifts
        self.shift_utc_plus_1 = self.Shift.create(
            {
                "name": "LondonShift",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 22, 59, 59),
                "end_time": datetime.datetime(2027, 6, 6, 23, 0, 1),
                "tz": "Europe/London",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        self.shift_utc_plus_2 = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 22, 0, 1),
                "end_time": datetime.datetime(2027, 6, 7, 0, 0, 1),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )

    def test_compute_volunteer_ids(self):
        """Test that the volunteer_ids are correctly computed
        2 participation confirmed, 1 participation canceled"""

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
        """Test that the shift is one day
        start_time = 2027-06-06 23:59:58
        end_time = 2027-06-06 23:59:59
        shift created with tz UTC
        expected is_one_day = True"""

        shift_utc = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 23, 59, 58),
                "end_time": datetime.datetime(2027, 6, 6, 23, 59, 59),
                "tz": "UTC",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )
        self.assertTrue(shift_utc.is_one_day)

        # Test that the shift is one day
        # start_time = 2027-06-06 23:59:59
        # end_time = 2027-06-07 00:00:01
        # shift created with tz UTC
        # expected is_one_day = False

        shift_utc = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 23, 59, 59),
                "end_time": datetime.datetime(2027, 6, 7, 0, 0, 1),
                "tz": "UTC",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )
        self.assertFalse(shift_utc.is_one_day)

    def test_compute_time_located(self):
        """Test that the start_time_located and end_time_located
        are correctly computed with specific timezone
        shift created with timezone Europe/London, UTC+1 summer time
        UTC start_time = 2027-06-06 22:59:59
        expected start_time_located = 2027-06-06 23:59:59
        UTC end_time = 2027-06-06 23:00:01
        expected end_time_located = 2027-06-07 00:00:01"""

        self.assertFalse(self.shift_utc_plus_1.is_one_day)

        # Shift created with timezone Europe/Brussels, UTC+2 summer time
        # UTC start_time = 2027-06-06 22:00:01
        # expected start_time_located = 2027-06-07 00:00:01
        # UTC end_time = 2027-06-07 00:00:01
        # expected end_time_located = 2027-06-07 02:00:01

        self.assertTrue(self.shift_utc_plus_2.is_one_day)

    def test_reduce_max_volunteer_equals_zero(self):
        """Test that it is possible to reduce max_volunteer_nb to 0"""

        with self.assertRaises(CheckViolation):
            self.shift_utc_plus_2.write(
                {
                    "max_volunteer_nb": 0,
                }
            )

    def test_reduce_max_volunteer_under_confirmed_participation(self):
        """Test that it is possible to reduce max_volunteer_nb
        under the number of confirmed participation
        2 participation confirmed, max_volunteer_nb set to 1"""

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
        """Test that the remaining slots are correctly computed
        1 participation confirmed, max_volunteer_nb = 2, remaining_slots = 1"""

        self.assertEqual(self.shift_max_2.remaining_slots, 1)

    def test_compute_remaining_slots_with_canceled_participation(self):
        """Test that the remaining slots are correctly computed
        when there is a canceled participation
        1 participation confirmed, 1 participation canceled,
        max_volunteer_nb = 2, remaining_slots = 1"""

        self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "canceled",
            }
        )
        self.assertEqual(self.shift_max_2.remaining_slots, 1)

    def test_volunteer_cannot_confirm_twice_for_same_shift(self):
        """Test that it is possible to create multiple participation
        for the same volunteer
        1 participation confirmed,
        1 participation confirmed for the same volunteer,
        nb_max_volunteer = 2"""

        with self.assertRaises(ValidationError):
            self.shift_max_2.write(
                {
                    "volunteer_participation_ids": [
                        Command.create({"volunteer_id": self.volunteer_confirmed.id}),
                    ]
                }
            )
