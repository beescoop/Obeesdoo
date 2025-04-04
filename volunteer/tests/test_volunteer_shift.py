from psycopg2.errors import CheckViolation

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import datetime

from .test_volunteer_common import TestVolunteerCommon


class TestShift(TestVolunteerCommon):
    def setUp(self):
        super().setUp()
        self.shift_utc_plus_1 = self.Shift.create(
            {
                "name": "LondonShift",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 22, 59, 59),
                "end_time": datetime.datetime(2027, 6, 6, 23, 00, 1),
                "tz": "Europe/London",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        self.shift_utc_plus_2 = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 00, 00, 1),
                "end_time": datetime.datetime(2027, 6, 6, 2, 00, 1),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )

    # Test is_one_day
    def test_is_one_day_with_tz__true(self):
        """Test if the shift is one day
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

    def test_is_one_day_false(self):
        """Test if the shift is one day
        start_time = 2027-06-06 23:59:59
        end_time = 2027-06-07 00:00:01
        shift created with tz UTC
        expected is_one_day = False"""

        shift_utc = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2027, 6, 6, 23, 59, 59),
                "end_time": datetime.datetime(2027, 6, 7, 00, 00, 1),
                "tz": "UTC",
                "max_volunteer_nb": 1,
                "type_id": self.type1.id,
            }
        )
        self.assertFalse(shift_utc.is_one_day)

    # Test compute located with is_one_day
    def test_compute_time_located_is_one_day_false(self):
        """Test if the start_time_located and end_time_located
        are correctly computed with specific timezone
        shift created with timezone Europe/London, UTC+1 summer time
        UTC start_time = 2027-06-06 22:59:59
        expected start_time_located = 2027-06-06 23:59:59
        UTC end_time = 2027-06-06 23:00:01
        expected end_time_located = 2027-06-07 00:00:01"""

        self.assertFalse(self.shift_utc_plus_1.is_one_day)

    def test_compute_time_located_is_one_day_true(self):
        """Test if the start_time_located and end_time_located
        are correctly computed with specific timezone
        shift created with timezone Europe/Brussels, UTC+2 summer time
        UTC start_time = 2027-06-06 22:00:01
        expected start_time_located = 2027-06-07 00:00:01
        UTC end_time = 2027-06-07 00:00:01
        expected end_time_located = 2027-06-07 02:00:01"""

        self.assertTrue(self.shift_utc_plus_2.is_one_day)

    # Test max_volunteer_nb
    def test_reduce_max_volunteer_equals_zero(self):
        """Test if it is possible to reduce max_volunteer_nb to 0"""

        with self.assertRaises(CheckViolation):
            self.shift_utc_plus_2.write(
                {
                    "max_volunteer_nb": 0,
                }
            )

    def test_reduce_max_volunteer_under_confirmed_participation(self):
        """Test if it is possible to reduce max_volunteer_nb
        under the number of confirmed participations
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

    # Tests remaining_slots
    def test_remaining_slots_confirmed_participation(self):
        """Test if the remaining slots are correctly computed
        1 participation confirmed, max_volunteer_nb = 2, remaining_slots = 1"""

        self.assertEqual(self.shift_max_2.remaining_slots, 1)

    def test_remaining_slots_with_canceled_participation(self):
        """Test if the remaining slots are correctly computed
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

    # Test unique participation constraint
    def test_unique_participation(self):
        """Test if it is possible to create multiple participations
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
