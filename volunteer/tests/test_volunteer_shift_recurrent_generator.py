# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import AccessError, ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGenerator(TestVolunteerGeneratorSubscriptionCommon):
    def setUp(self):
        super().setUp()

    def test_reduce_max_volunteer_under_nb_subscription(self):
        """Test that reducing max_volunteer_nb under the max number of existing
        subscriptions is not allowed"""
        # Setup creates 2 overlapping subscriptions (max 2 on same day)
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "max_volunteer_nb": 1,
                }
            )

    def test_subscription_for_the_same_volunteer_at_the_same_period_not_allowed(self):
        """Test that creating a subscription for the same volunteer
        at the same period is not allowed"""
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "volunteer_subscription_ids": [
                        Command.create(
                            {
                                "start_date": date(2025, 1, 6),
                                "end_date": date(2025, 1, 8),
                                "volunteer_id": self.volunteer_test_0.id,
                            }
                        ),
                        Command.create(
                            {
                                "start_date": date(2025, 1, 7),
                                "end_date": date(2025, 1, 9),
                                "volunteer_id": self.volunteer_test_0.id,
                            }
                        ),
                    ]
                }
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

    def test_create_participation_volunteer_already_subscribed_not_allowed(self):
        """Test that creating a participation for a volunteer
        already subscribed at the same period is not allowed"""
        # There is already a subscription for volunteer_test_0
        # from 2025/1/2 to 2025/1/4
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        shift_3 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 3, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        with self.assertRaises(ValidationError):
            self.Participation.create(
                {
                    "shift_id": shift_3.id,
                    "volunteer_id": self.volunteer_test_0.id,
                    "registration_state": "confirmed",
                }
            )

    def test_modify_until_date(self):
        """Test that modifying until_date is not allowed
        if there are subscriptions after the new until_date"""
        # Start_date generator : 2024/1/1
        # Until_date generator : 2026/12/24
        # There are subscriptions in 2025
        self.gen_each_day_max_2_vol.write({"until_date": False})
        # Reducing until_date to 2024 should be rejected
        # since there are subscriptions in 2025
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write({"until_date": date(2024, 1, 1)})

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

    def test_until_date_before_start_date_not_allowed(self):
        """Test that creating or modifying a generator with
        until_date before start_date is not allowed"""
        with self.subTest("Create generator with until_date before start_date"):
            with self.assertRaises(ValidationError):
                self.Generator.create(
                    {
                        "name": "GenInvalid",
                        "state": "draft",
                        "until_date": date(2023, 12, 24),
                        "interval_type": "days",
                        "interval": 1,
                        "start_time": datetime(2024, 1, 1, 10, 5),
                        "end_time": datetime(2024, 1, 1, 12, 5),
                        "tz": "Europe/Brussels",
                        "max_volunteer_nb": 3,
                        "type_id": self.type1.id,
                    }
                )
        with self.subTest("Modify generator to have until_date before start_date"):
            # Start_date is 2024/1/1
            with self.assertRaises(ValidationError):
                self.gen_each_day_max_2_vol.write(
                    {
                        "until_date": date(2023, 12, 24),
                    }
                )

    def test_cancel_generator_with_sub_allowed(self):
        """Test that canceling a generator is not blocked by
        dates constraints and that subscriptions end_date are set to today"""
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        # Check that subscriptions end_date is set to today
        self.assertEqual(self.sub_2_to_4_test0_max2.end_date, date(2025, 1, 1))
        self.assertEqual(self.sub_1_to_5_test1_max2.end_date, date(2025, 1, 1))

    def test_modification_on_confirmed_generator_not_allowed(self):
        """Test that modifying fields of a confirmed generator is not allowed"""
        # Confirmed that modifying fields of a draft generator is allowed
        self.gen_without_sub_2025_no_until.write(
            {
                "until_date": date(2026, 1, 1),
                "start_time": datetime(2025, 1, 1, 13, 0),
                "end_time": datetime(2025, 1, 1, 13, 0),
                "max_volunteer_nb": 3,
            }
        )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write({"max_volunteer_nb": 4})
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write({"until_date": date(2026, 1, 3)})

        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {"start_time": datetime(2025, 1, 1, 15, 0)}
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {"end_time": datetime(2025, 1, 1, 16, 0)}
            )
        with self.assertRaises(AccessError):
            self.gen_without_sub_2025_no_until.with_user(self.user_user).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )
        # Test authorized action : subscription management via notebook
        self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
            {
                "volunteer_subscription_ids": [
                    Command.create(
                        {
                            "start_date": date(2025, 1, 1),
                            "end_date": date(2025, 1, 2),
                            "volunteer_id": self.volunteer_test.id,
                        }
                    )
                ]
            }
        )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "volunteer_subscription_ids": [
                    Command.create(
                        {
                            "start_date": date(2025, 1, 3),
                            "end_date": date(2025, 1, 4),
                            "volunteer_id": self.volunteer_test_0.id,
                        }
                    )
                ]
            }
        )

    def test_modification_on_canceled_generator_not_allowed(self):
        """Test that modifying fields of a canceled generator is not allowed"""
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {
                    "max_volunteer_nb": 4,
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {
                    "until_date": date(2026, 1, 3),
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {
                    "start_time": datetime(2025, 1, 1, 15, 0),
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.write(
                {
                    "end_time": datetime(2025, 1, 1, 16, 0),
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.with_user(self.user_user).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )

    def test_subscription_management_via_notebook_blocked_on_canceled_generator(self):
        """Test that subscription management via notebook is blocked
        on a canceled generator"""
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
                {
                    "volunteer_subscription_ids": [
                        Command.create(
                            {
                                "start_date": date(2025, 1, 1),
                                "end_date": date(2025, 1, 1),
                                "volunteer_id": self.volunteer_test.id,
                            }
                        )
                    ]
                }
            )
        with self.assertRaises(ValidationError):
            self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
                {
                    "volunteer_subscription_ids": [
                        Command.create(
                            {
                                "start_date": date(2025, 1, 3),
                                "end_date": date(2025, 1, 4),
                                "volunteer_id": self.volunteer_test_0.id,
                            }
                        )
                    ]
                }
            )

    def test_write_fields_during_generator_cancellation_not_allowed(self):
        """Test that modifying other fields while setting state to canceled is not allowed"""
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
                {
                    "state": "canceled",
                    "max_volunteer_nb": 4,
                    "start_time": datetime(2025, 1, 10, 15, 0),
                    "end_time": datetime(2025, 1, 10, 16, 0),
                }
            )

    def test_draft_generator_write_permissions_by_role(self):
        """Test that field modifications on a draft generator
        are allowed for admins only, except for subscription management
        for managers"""
        # Generator in draft state, without subscriptions
        # User blocked for all modifications
        with self.assertRaises(AccessError):
            self.gen_without_sub_2025_no_until.with_user(self.user_user).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )
        # Manager blocked for field modifications
        with self.assertRaises(AccessError):
            self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
                {
                    "max_volunteer_nb": 4,
                    "until_date": date(2026, 1, 3),
                    "start_time": datetime(2025, 1, 1, 15),
                    "end_time": datetime(2025, 1, 1, 16, 0),
                    "type_id": self.type2.id,
                }
            )
        # Manager allowed for subscription management only
        # (from notebook)
        self.gen_without_sub_2025_no_until.with_user(self.user_manager).write(
            {
                "volunteer_subscription_ids": [
                    Command.create(
                        {
                            "start_date": date(2025, 1, 10),
                            "end_date": date(2025, 1, 12),
                            "volunteer_id": self.volunteer_test.id,
                        }
                    )
                ]
            }
        )
        # Admin allowed for field modifications
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "max_volunteer_nb": 4,
                "until_date": date(2026, 1, 3),
            }
        )
