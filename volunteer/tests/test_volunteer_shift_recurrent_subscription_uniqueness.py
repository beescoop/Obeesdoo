# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
from datetime import date, datetime

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionUniqueness(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_create_write_sub_for_same_volunteer_different_period_allowed(self):
        """Test that creating or writing a subscription for the same volunteer
        with non-overlapping period is allowed including subscriptions
        without end_date"""
        # Generator has no until_date
        # There is no subscription in setUp()
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # No overlap, subscription allowed
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # No overlap, writing end_date allowed
        sub.write(
            {
                "end_date": date(2025, 1, 8),
            }
        )

    def test_create_sub_same_volunteer_no_overlap_allowed(self):
        """Test that creating a subscription for the same volunteer
        with a non-overlapping period is allowed and doesn't block subscriptions
        for other volunteers, even if their subscription overlaps with at least
        two overlapping subscriptions of the first volunteer."""
        # Generator has no until_date
        # There is no subscription in setUp()
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # Create a subscription for another volunteer that covers
        # at least 2 overlapping subscriptions of the first volunteer
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": date(2025, 1, 12),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )

    def test_create_and_write_multiple_subscriptions_different_generator(self):
        """Test creating multiple subscriptions at once on different generator."""
        # Create multi subscriptions with different generator
        vals_list = [
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 7),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            },
            {
                "start_date": date(2025, 1, 8),
                "end_date": date(2025, 1, 9),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 11),
                "volunteer_id": self.volunteer_confirmed2.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            },
        ]
        subscriptions = self.Subscription.create(vals_list)
        self.assertEqual(len(subscriptions), 3)

    def test_create_overlap_sub_same_volunteer_without_end_not_allowed(self):
        """Test that creating a subscription with an overlapping period
        for the same volunteer is not allowed,
        even when the new subscription has no end_date"""
        # Generator has no until_date
        # There is no subscription in setUp()
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 3),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )

    def test_write_overlap_sub_same_volunteer_without_end_not_allowed(self):
        """Test that updating a subscription to create an overlapping period
        for the same volunteer is not allowed,
        including when removing the end_date or changing the start_date"""
        # Generator has no until_date
        # There is no subscription in setUp()
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # No overlap, subscription allowed
        sub1 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # Writing end_date to False to create overlap not allowed
        with self.subTest("Writing end_date to create overlap not allowed"):
            with self.assertRaises(ValidationError):
                sub.write(
                    {
                        "end_date": False,
                    }
                )
        with self.subTest("Writing start_date to create overlap not allowed"):
            # Writing start_date to create overlap not allowed
            with self.assertRaises(ValidationError):
                sub1.write(
                    {
                        "start_date": date(2025, 1, 4),
                    }
                )

    def test_create_multiple_sub_same_volunteer_not_allowed(self):
        """Test that creating multiple subscriptions for the same volunteer
        with overlapping periods is not allowed"""
        # Generator start date is 2025-01-01
        # There is no subscription in setUp()
        vals_list = [
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            },
            {
                "start_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            },
        ]
        with self.assertRaises(ValidationError):
            self.Subscription.create(vals_list)

    def test_changing_volunteer_of_subscription_not_allowed(self):
        """Test that changing the volunteer of an existing subscription is not allowed."""
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 12),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        with self.assertRaises(ValidationError):
            sub.write({"volunteer_id": self.volunteer_confirmed.id})

    def test_infinite_subscription_start_after_generator_until_date_not_allowed(self):
        """Test that creating a subscription without end_date is not allowed
        when generator has an until_date"""
        # Generator has until_date at 2026-12-24
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2026, 12, 25),
                    "end_date": False,
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_each_day_max_2_vol.id,
                }
            )

    @unittest.skip(
        "Known limitation: Shifts with duration greater than 1 day not handled"
    )
    def test_multi_day_shift_limitation(self):
        """Test demonstrates a known limitation with multi-day shifts.

        Example: A subscription ending on day X should generate participation
        for shifts starting on day X, even if the shift extends beyond day X.
        Other edge cases likely exist but haven't been fully verified.
        """

        gen_shift_2_days = self.Generator.create(
            {
                "name": "Generator with 2 days shift",
                "state": "draft",
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2025, 1, 10, 23, 0),
                "end_time": datetime(2025, 1, 11, 1, 0),
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )

        gen_shift_2_days.with_user(self.user_admin).write({"state": "confirmed"})

        # Create a subscription ending on the same day as the start of the shift
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": gen_shift_2_days.id,
            }
        )

        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 10, 23, 0)),
                ("generator_id", "=", gen_shift_2_days.id),
            ]
        )

        participation = self.Participation.search(
            [
                ("shift_id", "=", shift.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )

        # Check that participation for shift on 2025-01-10 23:00 is created
        # despite the shift ending on 2025-01-11
        self.assertEqual(len(participation), 1)

    @unittest.skip(
        "Known limitation: Multi-record validation incorrectly rejects valid modifications"
    )
    def test_write_multiple_subscriptions_double_counting_same_modification(self):
        """Test demonstrates validation incorrectly rejecting a valid multi-record modification

        This should PASS but currently FAILS due to double-counting limitation.
        The modification is valid (respects unicity and capacity)
        but validation sees false conflicts.

        Currently, the first error raised is the unicity constraint.
        """
        # Initial state: 2 subscriptions on different periods, no conflicts
        sub1 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 12),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        sub2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 8),
                "end_date": date(2025, 1, 9),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )

        # Batch modification: same modification for both subscriptions (10th to 15th)
        # Expected final state: 2 subscriptions from 10th to 15th
        # = max 2 volunteers per day = Valid
        # Limitation behavior: During validation, the system counts subscriptions
        # from volunteer_subscription_ids (which still contains old values:
        # sub1(10-12) + sub2(8-9)) plus new requested values
        # (sub1(10-15) + sub2(10-15)).
        # However, sub_to_exclude only removes one old subscription per iteration
        # (e.g., when validating sub1, only sub1_old(10-12) is excluded), leading to
        # triple counting on overlapping dates
        # (e.g., on 10th: sub1_old(10-12) + sub1_new(10-15) +
        # sub2_new(10-15) - sub1_old(10-12) excluded = 2,
        # but when validating sub2: sub1_old(10-12) + sub1_new(10-15) + sub2_new(10-15)
        # - sub2_old(8-9) excluded = 3 > max 2).

        # This modification should succeed (respects capacity and unicity)
        # but currently fails at first validation step (unicity error)
        # due to double-counting limitation explained above.
        (sub1 + sub2).write(
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 15),
            }
        )
