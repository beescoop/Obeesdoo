# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorGeneration(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_generate_shifts_with_past_start_date(self):
        """Test that shifts are generated from today
        when generator start_date is in the past
        """
        # Generator starts in the past (2024-01-01), today freeze to 2025-01-01,
        # shifts should be generated starting from today only
        self.gen_with_past_start.write({"state": "confirmed"})
        shifts = self.Shift.search([("generator_id", "=", self.gen_with_past_start.id)])
        self.assertEqual(shifts[0].start_time.date(), date.today())

    def test_generate_shifts_from_start_date_future(self):
        """Test that shifts are generated from the configured start_date
        when it's in the future
        """
        # Today is frozen to 2025-01-01
        self.gen_today_to_infinite_empty.write(
            {
                "start_time": datetime(2025, 2, 1, 10, 5),
                "end_time": datetime(2025, 2, 1, 12, 5),
            }
        )
        self.gen_today_to_infinite_empty.write({"state": "confirmed"})
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_today_to_infinite_empty.id)]
        )
        start_date = self.gen_today_to_infinite_empty.start_time.date()
        self.assertEqual(shifts[0].start_time.date(), start_date)

    def test_generate_right_number_of_shifts_generator_with_until_date(self):
        """Test that the right number of shifts are generated
        based on until_date and not on number of occurrences
        """
        # Between 2025-01-01 and 2025-01-05 there are 5 occurrences
        # and not 10 like number of occurrences
        self.gen_today_to_infinite_empty.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
                "until_date": date(2025, 1, 5),
            }
        )
        self.gen_today_to_infinite_empty.write({"state": "confirmed"})
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_today_to_infinite_empty.id)]
        )
        self.assertEqual(len(shifts), 5)

    def test_generate_right_number_of_shifts_generator_without_until_date(self):
        """Test that the right number of shifts are generated
        based on number of occurrences since there is no until_date
        """
        # Number of occurrences is 10
        # Today is frozen to 2025-01-01, so shifts will be generated from this date
        self.gen_today_to_infinite_empty.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
            }
        )
        self.gen_today_to_infinite_empty.write({"state": "confirmed"})
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_today_to_infinite_empty.id)]
        )
        self.assertEqual(len(shifts), 10)

    def test_generate_shifts_with_right_period(self):
        """Test that the shifts are generated with the right start and end time"""
        self.gen_today_to_infinite_empty.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
                "until_date": date(2025, 1, 6),
            }
        )
        self.gen_today_to_infinite_empty.write({"state": "confirmed"})
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_today_to_infinite_empty.id)]
        )
        expected_start = datetime(2025, 1, 1, 10, 5)
        expected_end = datetime(2025, 1, 1, 12, 5)
        # Each generated shift must strictly match the configured time slot
        # with the correct interval applied between occurrences
        for shift in shifts:
            self.assertEqual(shift.start_time, expected_start)
            self.assertEqual(shift.end_time, expected_end)
            expected_start = (
                expected_start + self.gen_today_to_infinite_empty._get_interval_delta()
            )
            expected_end = (
                expected_end + self.gen_today_to_infinite_empty._get_interval_delta()
            )

    def test_generate_shifts_different_intervals(self):
        """Test shift generation with different interval types"""
        intervals = [
            (
                "days",
                3,
                [
                    datetime(2025, 1, 1, 10, 0),
                    datetime(2025, 1, 4, 10, 0),
                    datetime(2025, 1, 7, 10, 0),
                ],
            ),
            (
                "weeks",
                2,
                [
                    datetime(2025, 1, 1, 10, 0),
                    datetime(2025, 1, 15, 10, 0),
                    datetime(2025, 1, 29, 10, 0),
                ],
            ),
            (
                "months",
                3,
                [
                    datetime(2025, 1, 1, 10, 0),
                    datetime(2025, 4, 1, 10, 0),
                    datetime(2025, 7, 1, 10, 0),
                ],
            ),
            (
                "years",
                1,
                [
                    datetime(2025, 1, 1, 10, 0),
                    datetime(2026, 1, 1, 10, 0),
                    datetime(2027, 1, 1, 10, 0),
                ],
            ),
        ]
        for interval_type, interval_value, expected_start in intervals:
            with self.subTest(interval_type=interval_type, interval=interval_value):
                # Create new generator for each test
                generator = self.Generator.create(
                    {
                        "name": f"Test each {interval_value} {interval_type}",
                        "state": "draft",
                        "interval_type": interval_type,
                        "interval": interval_value,
                        "start_time": datetime(2025, 1, 1, 10, 0),
                        "end_time": datetime(2025, 1, 1, 12, 0),
                        "max_volunteer_nb": 3,
                        "type_id": self.type1.id,
                        "tz": "Europe/Brussels",
                    }
                )
                generator.write({"state": "confirmed"})
                shifts = self.Shift.search(
                    [("generator_id", "=", generator.id)], order="start_time"
                )
                self.assertGreaterEqual(len(shifts), len(expected_start))
                # Verify interval progression on first 3 shifts
                for i, expected_date in enumerate(expected_start):
                    self.assertEqual(shifts[i].start_time, expected_date)
