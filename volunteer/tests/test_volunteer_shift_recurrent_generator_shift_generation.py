# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorGeneration(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_generate_shifts_from_today(self):
        """Test that shifts are generated from today if
        start_date is in the past"""
        # Start_date generator : 2023/1/1
        # Today is frozen to 2025/1/1
        self.gen_with_past_start.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        shifts = self.Shift.search([("generator_id", "=", self.gen_with_past_start.id)])
        start_date = date.today()
        for shift in shifts:
            self.assertEqual(shift.start_time.date(), start_date)
            start_date += self.gen_with_past_start._get_interval_delta()

    def test_generate_shifts_from_start_date_future(self):
        """Test that shifts are generated from start_date
        if start_date is in the future"""
        # Today is frozen to 2025/1/1
        self.gen_without_sub_2025_no_until.write(
            {
                "start_time": datetime(2025, 2, 1, 10, 5),
                "end_time": datetime(2025, 2, 1, 12, 5),
            }
        )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_without_sub_2025_no_until.id)]
        )
        start_date = self.gen_without_sub_2025_no_until.start_time.date()
        for shift in shifts:
            self.assertEqual(shift.start_time.date(), start_date)
            start_date += self.gen_without_sub_2025_no_until._get_interval_delta()

    def test_generate_right_number_of_shifts_with_until_date(self):
        """Test that the right number of shifts are generated
        based on until_date and not on number of occurrences"""
        # Between 2025/1/1 and 2025/1/5 there are 5 occurrences
        # and not 10 like number of occurrences
        self.gen_each_day_max_2_vol.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
                "until_date": date(2025, 1, 5),
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_each_day_max_2_vol.id)]
        )
        self.assertEqual(len(shifts), 5)

    def test_generate_right_number_of_shifts_without_until_date(self):
        """Test that the right number of shifts are generated
        based on number of occurrences since there is no until_date"""
        # Number of occurrences is 10
        # Today is frozen to 2025/1/1
        self.gen_each_day_max_2_vol.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_each_day_max_2_vol.id)]
        )
        self.assertEqual(len(shifts), 10)

    def test_generate_shift_with_right_start_end_time(self):
        """Test that the shifts are generated with the right start and end time"""
        self.gen_each_day_max_2_vol.write(
            {
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
                "until_date": date(2025, 1, 6),
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        shifts = self.Shift.search(
            [("generator_id", "=", self.gen_each_day_max_2_vol.id)]
        )
        expected_start = datetime(2025, 1, 1, 10, 5)
        expected_end = datetime(2025, 1, 1, 12, 5)
        for shift in shifts:
            self.assertEqual(shift.start_time, expected_start)
            self.assertEqual(shift.end_time, expected_end)
            expected_start = (
                expected_start + self.gen_each_day_max_2_vol._get_interval_delta()
            )
            expected_end = (
                expected_end + self.gen_each_day_max_2_vol._get_interval_delta()
            )

    def test_determine_furthest_end_date_no_until_date_multiple_sub_no_end(self):
        """Test that the furthest end date is correctly determined
        when there are multiple subscriptions without end_date
        and the generator has no until_date.
        For confirmed generators, generated shifts take precedence
        over subscription start dates."""
        # Create multiple subscriptions without end_date
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": False,
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 5),
                "end_date": False,
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        with self.subTest("No participation"):
            # Furthest end date should be furthest start_date (2025/01/05)
            # + 1 day since there are only subscriptions without end_date
            # and no until_date on the generator (his start_time is 2025/01/01)
            self.assertEqual(
                self.gen_without_sub_2025_no_until.determine_furthest_end_date(),
                date(2025, 1, 6),
            )
        with self.subTest("With participation before last subscription start_date"):
            self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
                {
                    "state": "confirmed",
                }
            )
            shift_2 = self.Shift.search(
                [
                    (
                        "start_time",
                        "=",
                        datetime(2025, 1, 2, 10, 5),
                    ),
                    ("generator_id", "=", self.gen_without_sub_2025_no_until.id),
                ]
            )
            self.Participation.create(
                {
                    "shift_id": shift_2.id,
                    "volunteer_id": self.volunteer_confirmed.id,
                    "registration_state": "confirmed",
                }
            )
            # Furthest end date should be last generated shift end_time + 1 day
            # since generator is confirmed and has generated shifts (2025/01/01 to 2025/01/10)
            # after last subscription start_date (2025/01/05)
            self.assertEqual(
                self.gen_without_sub_2025_no_until.determine_furthest_end_date(),
                date(2025, 1, 11),
            )
        with self.subTest("With participation after last subscription start_date"):
            shift_10 = self.Shift.search(
                [
                    (
                        "start_time",
                        "=",
                        datetime(2025, 1, 10, 10, 5),
                    ),
                    ("generator_id", "=", self.gen_without_sub_2025_no_until.id),
                ]
            )
            self.Participation.create(
                {
                    "shift_id": shift_10.id,
                    "volunteer_id": self.volunteer_confirmed2.id,
                    "registration_state": "confirmed",
                }
            )
            # Furthest end date should be last generated shift end_time + 1 day (2025/01/11)
            # since confirmed generator prioritizes generated shifts
            # over individual participation
            self.assertEqual(
                self.gen_without_sub_2025_no_until.determine_furthest_end_date(),
                date(2025, 1, 11),
            )
