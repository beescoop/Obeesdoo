# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionParticipation(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_subscription_invalid_date_ranges_rejected(self):
        """Test that creating a subscription with invalid date ranges is rejected."""
        # Time frozen at 2025-01-01 10:00, which is considered as "today" during tests
        # Generator setup with past start date starting at 2023/1/1 and until date 2024/12/24
        # Subscription in the past should be rejected even if within generator range
        with self.subTest("Past start date"):
            with self.assertRaises(ValidationError):
                self.Subscription.create(
                    {
                        "start_date": date(2024, 12, 10),
                        "end_date": date(2024, 12, 12),
                        "volunteer_id": self.volunteer_test.id,
                        "generator_id": self.gen_with_past_start.id,
                    }
                )
        # Change until_date of generator to future date
        # to allow future testing of subscription date ranges
        self.gen_with_past_start.write({"until_date": date(2025, 3, 31)})
        # Subscription outside generator range should be rejected
        with self.subTest("Outside generator range"):
            with self.assertRaises(ValidationError):
                self.Subscription.create(
                    {
                        "start_date": date(2025, 3, 25),
                        "end_date": date(2025, 4, 26),
                        "volunteer_id": self.volunteer_test_0.id,
                        "generator_id": self.gen_with_past_start.id,
                    }
                )
        # Subscription start date after end date should be rejected
        with self.subTest("Start date after end date"):
            with self.assertRaises(ValidationError):
                self.Subscription.create(
                    {
                        "start_date": date(2025, 3, 10),
                        "end_date": date(2025, 3, 8),
                        "volunteer_id": self.volunteer_test_0.id,
                        "generator_id": self.gen_with_past_start.id,
                    }
                )
        # Subscription start date with end date False should be allowed
        # if start_date is before until_date of generator when defined
        with self.subTest("Start date before until_date without end date allowed"):
            self.Subscription.create(
                {
                    "start_date": date(2025, 3, 10),
                    "end_date": False,
                    "volunteer_id": self.volunteer_test_0.id,
                    "generator_id": self.gen_with_past_start.id,
                }
            )
        # Subscription start date after until_date generator
        # and without end date should be rejected
        with self.subTest("Start date after until_date date without end_date rejected"):
            with self.assertRaises(ValidationError):
                self.Subscription.create(
                    {
                        "start_date": date(2025, 4, 1),
                        "end_date": False,
                        "volunteer_id": self.volunteer_test_0.id,
                        "generator_id": self.gen_with_past_start.id,
                    }
                )

    def test_create_subscription_with_past_start_date_not_allowed(self):
        """Test that creating a subscription with start_date in past is not allowed"""
        # Time frozen at 2025-01-01
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2024, 12, 1),
                    "end_date": date(2025, 12, 5),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )

    def test_start_date_past_validation_only_when_explicitly_modified(self):
        """Test that start_date validation only triggers
        when explicitly modified, allowing modification of end_date
        even when start_date becomes past due to time passing."""
        # Time frozen at 2025-01-01
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 2, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # Move time forward to 2025-03-01 where start_date is now in the past
        with freeze_time("2025-03-01 10:00:00"):
            # Modify end_date only, should succeed
            sub.write({"end_date": date(2025, 3, 10)})
            # Explicitly modify start_date to past, should fail
            with self.assertRaises(ValidationError):
                sub.write({"start_date": date(2025, 2, 15)})

    def test_generate_participation_with_until_date(self):
        """Test that participations are generated only up to the end_date of the subscription
        even if the generator has an until_date beyond the subscription end_date."""
        self.gen_each_day_max_2_vol.write(
            {
                "until_date": date(2025, 1, 10),
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 9),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        # Search shifts from 2025-01-06 to 2025-01-09 (4 shifts)
        # which is within subscription dates
        shifts = self.Shift.search(
            [
                ("start_time", ">=", datetime(2025, 1, 6)),
                ("start_time", "<", datetime(2025, 1, 10)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        self.assertEqual(len(shifts), 4)
        # Check that participation are created for these shifts
        parts = self.Participation.search(
            [
                ("shift_id", "in", shifts.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(parts), 4)
        # Check that participation are not created beyond end_date of subscription
        shifts_beyond = self.Shift.search(
            [
                ("start_time", ">=", datetime(2025, 1, 10)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        self.assertEqual(len(shifts_beyond), 1)
        parts_beyond = self.Participation.search(
            [
                ("shift_id", "in", shifts_beyond.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(parts_beyond), 0)

    def test_generate_participation_without_generator_until_date(self):
        """Test that participations are generated up to nb_occurrence
        when the generator has no until_date and the subscription has no end_date."""
        self.gen_each_day_max_2_vol.write(
            {
                "until_date": False,
            }
        )
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        # Create a subscription without end date
        sub_no_end = self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": False,
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        # Start date of generator is 2024-01-01,
        # so generator start generates from today (frozen at 2025-01-01)
        # until nb_occurrence (10) means 2025-01-10
        shifts = self.Shift.search(
            [
                ("start_time", ">=", sub_no_end.start_date),
                ("start_time", "<", date(2025, 1, 11)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        # From start subscription : 2025-01-06
        # to last date shift generated :2025-01-10
        # there is 5 shifts generated
        self.assertEqual(len(shifts), 5)
        all_participation = self.Participation.search(
            [
                ("shift_id", "in", shifts.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        # Check that participation are created for these shifts
        self.assertEqual(len(all_participation), 5)

    def test_autocancel_participation_covered_by_new_sub_same_volunteer(self):
        """Test that a participation is auto-canceled when a new subscription
        is created that covers the date of the participation for the same volunteer."""
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 7, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_3_vol.id),
            ]
        )
        part1 = self.Participation.create(
            {
                "shift_id": shift.id,
                "volunteer_id": self.volunteer_test_0.id,
                "registration_state": "confirmed",
            }
        )
        self.assertEqual(
            part1.registration_state,
            "confirmed",
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 8),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        self.assertEqual(
            part1.registration_state,
            "canceled",
        )

    def test_autocancel_participation_covered_by_modified_sub_same_volunteer(self):
        """Test that a participation is auto-canceled when an existing subscription
        is modified to cover the date of the participation for the same volunteer."""
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        shift2 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 8, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_3_vol.id),
            ]
        )
        part2 = self.Participation.create(
            {
                "shift_id": shift2.id,
                "volunteer_id": self.volunteer_test_1.id,
                "registration_state": "confirmed",
            }
        )
        self.assertEqual(
            part2.registration_state,
            "confirmed",
        )
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 4),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        # Extend subscription to cover participation date
        sub.write(
            {
                "end_date": False,
            }
        )
        self.assertEqual(
            part2.registration_state,
            "canceled",
        )

    def test_managing_cancel_or_create_participation(self):
        """Test managing canceling or creating participation when modifying
        a subscription end_date including setting it to None (no end)."""
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        # Create a subscription from 2025-01-07 with end date
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 7),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        # Modify end date to 2025-01-10
        sub.write({"end_date": date(2025, 1, 10)})
        # Check that participation are created for shift on 2025-01-08
        # which is within subscription dates
        shift_8 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 8, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        part_8_confirmed = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_8_confirmed), 1)
        # Reduce end date to 2025-01-07
        # needs to cancel participation on 2025-01-08
        sub.write({"end_date": date(2025, 1, 7)})
        part_8_canceled = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "canceled"),
            ]
        )
        # Check that participation for shift on 2025-01-08 is canceled
        # and there is no other confirmed participation for this shift
        # and volunteer
        self.assertEqual(len(part_8_canceled), 1)
        part_8 = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_8), 0)
        # Modify end date to None (no end)
        # needs to create participation after 2025-01-08 (check 2025-01-10)
        sub.write({"end_date": False})
        shift_10 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 10, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_2_vol.id),
            ]
        )
        part_10 = self.Participation.search(
            [
                ("shift_id", "=", shift_10.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_10), 1)

    def test_extend_past_subscription_with_missed_shifts_not_allowed(self):
        """Test that extending a subscription that ended in the past
        is not allowed when there are generated shifts between the old end date
        and today for a confirmed generator."""
        # Create a generator and confirm it to generate shifts
        generator = self.Generator.create(
            {
                "name": "TestPastExtension",
                "state": "draft",
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2025, 1, 1, 10, 0),
                "end_time": datetime(2025, 1, 1, 12, 0),
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        # Create a subscription in future that will end in the past
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 5),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": generator.id,
            }
        )
        # Confirm generator to generate shifts
        generator.with_user(self.user_admin).write({"state": "confirmed"})
        # Verify that reducing end_date is still allowed
        sub.write({"end_date": date(2025, 1, 8)})
        # Freeze time to 2025-01-10, so subscription ended in the past
        # and there are generated shifts between end_date and today
        with freeze_time("2025-01-10 10:00:00"):
            # Extend subscription end_date to a future date not allowed
            # because there are generated shifts between old end_date and today
            with self.assertRaises(ValidationError):
                sub.write({"end_date": date(2025, 1, 15)})
            # Extending subscription by setting end_date to False (infinite)
            # should also be rejected
            with self.assertRaises(ValidationError):
                sub.write({"end_date": False})

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
