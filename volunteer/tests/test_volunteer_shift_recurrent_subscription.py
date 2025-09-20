# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import unittest
from datetime import date, datetime

from freezegun import freeze_time

from odoo.exceptions import AccessError, ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscription(TestVolunteerGeneratorSubscriptionCommon):
    def setUp(self):
        super().setUp()

    def test_manager_can_create_write_subscription(self):
        """Test that a user with the 'Volunteer Manager' role can create
        a subscription on a generator in 'draft' and 'confirmed' state,
        but not on a generator in 'canceled' state."""
        sub = self.Subscription.with_user(self.user_manager).create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        sub.with_user(self.user_manager).write(
            {
                "end_date": date(2025, 1, 4),
            }
        )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.Subscription.with_user(self.user_manager).create(
            {
                "start_date": date(2025, 1, 5),
                "end_date": date(2025, 1, 7),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        sub.with_user(self.user_manager).write(
            {
                "start_date": date(2025, 1, 3),
            }
        )

    def test_user_cannot_create_write_subscription(self):
        """Test that a user with the 'Volunteer User' role cannot create
        or write a subscription on any generator state."""
        # Setup set runs all operations as admin by default
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        with self.assertRaises(AccessError):
            self.Subscription.with_user(self.user_user).create(
                {
                    "start_date": date(2025, 1, 10),
                    "end_date": date(2025, 1, 12),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        with self.assertRaises(AccessError):
            sub.with_user(self.user_user).write(
                {
                    "end_date": date(2025, 1, 4),
                }
            )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(AccessError):
            self.Subscription.with_user(self.user_user).create(
                {
                    "start_date": date(2025, 1, 10),
                    "end_date": date(2025, 1, 12),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        with self.assertRaises(AccessError):
            sub.with_user(self.user_user).write(
                {
                    "end_date": date(2025, 1, 6),
                }
            )

    def test_no_create_write_sub_on_canceled_generator(self):
        """Test that creating or writing a subscription on a generator
        in 'canceled' state is not allowed for any user role.
        Except writing end_date to today for admins only."""
        # Setup set runs all operations as admin by default
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.with_user(self.user_user).create(
                {
                    "start_date": date(2025, 1, 1),
                    "end_date": date(2025, 1, 2),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        with self.assertRaises(ValidationError):
            sub.with_user(self.user_user).write(
                {
                    "end_date": date(2025, 1, 1),
                }
            )
        with self.assertRaises(ValidationError):
            self.Subscription.with_user(self.user_manager).create(
                {
                    "start_date": date(2025, 1, 3),
                    "end_date": date(2025, 1, 5),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        with self.assertRaises(ValidationError):
            sub.with_user(self.user_manager).write(
                {
                    "end_date": date(2025, 1, 1),
                }
            )
        with self.assertRaises(ValidationError):
            self.Subscription.with_user(self.user_admin).create(
                {
                    "start_date": date(2025, 1, 6),
                    "end_date": date(2025, 1, 8),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        # Writing end_date to today is allowed for admins
        # Today is 2025-01-01 due to freeze_time
        with self.assertRaises(ValidationError):
            sub.with_user(self.user_admin).write(
                {
                    "end_date": date(2025, 1, 4),
                }
            )
        sub.with_user(self.user_admin).write(
            {
                "end_date": date(2025, 1, 1),
            }
        )

    def test_subscription_exceed_max_3_with_overlaps_not_allowed(self):
        """Test that creating a subscription that would exceed the max_volunteer_nb
        for any day in the subscription period is not allowed."""
        # There is already 3 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2024, 12, 3),
                    "end_date": date(2025, 1, 10),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )

    def test_subscription_exceed_max_3_with_overlaps_borders(self):
        """Test that creating a subscription that would exceed the max_volunteer_nb
        for any day in the subscription period is not allowed, even if it starts or ends
        on the border of existing subscriptions."""
        # There is already 3 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 1),
                    "end_date": date(2025, 1, 3),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 3),
                    "end_date": date(2025, 1, 5),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )

    def test_subscription_exceed_max_2_one_single_day(self):
        """Test that creating a subscription that would exceed the max_volunteer_nb
        for a single day is not allowed."""
        # There is already 2 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteer
        # 01/03 : 2 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 2),
                    "end_date": date(2025, 1, 2),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_2_vol.id,
                }
            )

    def test_subscription_without_overlaps_dont_exceed_max_3(self):
        """Test that creating a subscription that does not overlap with existing
        subscriptions and does not exceed max_volunteer_nb is allowed."""
        # There is already 3 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )

    def test_write_extend_subscription_causes_exceeding_max(self):
        """Test that extending an existing subscription that would cause the
        max_volunteer_nb to be exceeded is not allowed."""
        # There is already 3 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        new_sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        with self.assertRaises(ValidationError):
            new_sub.write(
                {
                    "end_date": date(2025, 1, 5),
                }
            )

    def test_create_sub_same_volunteer_no_overlap_allowed(self):
        """Test that creating a subscription for the same volunteer
        with a non-overlapping period is allowed and doesn't block subscriptions
        for other volunteers, even if their subscription overlaps with at leas
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

    def test_unsubscribe_allows_new_subscription(self):
        """Test that modifying an existing subscription to free up slots
        allows creating a new subscription that fits within the max_volunteer_nb."""
        # There is already 2 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteer
        # 01/03 : 2 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 3),
                    "end_date": date(2025, 1, 3),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_2_vol.id,
                }
            )
        # Reduce existing subscription to free up slot on 2025-01-3
        self.sub_1_to_5_test1_max2.write(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 1),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": date(2025, 1, 3),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

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

    def test_create_multiple_subscriptions_conflicts(self):
        """Test that creating multiple subscriptions at once that would
        exceed the max_volunteer_nb for any day is not allowed."""
        # There is no subscription in setUp() for 2025 january 6
        # max 2 volunteers for gen_each_day_max_2_vol
        vals_list_conflict_same_gen = [
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_confirmed2.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
        ]
        with self.assertRaises(ValidationError):
            self.Subscription.create(vals_list_conflict_same_gen)

    def test_write_multiple_subscriptions_conflicts(self):
        """Test that writing multiple subscriptions at once that would
        exceed the max_volunteer_nb for any day is not allowed."""
        # There is already 3 subscriptions created in setUp() for 2025 january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        sub1 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 7),
                "end_date": date(2025, 1, 7),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        sub2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 8),
                "end_date": date(2025, 1, 8),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        with self.assertRaises(ValidationError):
            (sub1 + sub2).write(
                {
                    "start_date": date(2025, 1, 1),
                    "end_date": date(2025, 1, 1),
                }
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
            sub.write({"end_date": date(2025, 2, 10)})
            # Explicitly modify start_date to past, should fail
            with self.assertRaises(ValidationError):
                sub.write({"start_date": date(2025, 1, 15)})

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

    def test_write_sub_end_date_from_none_to_defined_with_full_capacity_allowed(self):
        """Test that modifying end_date of a subscription from None to a defined date
        is allowed when max capacity is reached with other subscriptions without end_date
        Note : Integration test for _managing_cancel_or_create_participation
        with None end_date handling."""
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        # Create 3 subscriptions without end_date to reach max capacity
        sub1 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # Reducing end_date of one subscription should be allowed
        sub1.write({"end_date": date(2025, 1, 15)})

    def test_write_sub_start_date_with_full_capacity_reached_no_end_date_allowed(self):
        """Test that modifying start_date of a subscription is allowed
        when max capacity is reached with other subscriptions without end_date
        Note: Integration test: Validates the old_end_date=new_end_date
        fix in _managing_cancel_or_create_participation."""
        self.gen_without_sub_2025_no_until.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        # Create 3 subscriptions without end_date to reach max capacity
        sub1 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": False,
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_without_sub_2025_no_until.id,
            }
        )
        # Modifying start_date of one subscription should be allowed
        sub1.write({"start_date": date(2025, 1, 15)})

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
                "end_date": date(2025, 1, 8),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": generator.id,
            }
        )
        # Confirm generator to generate shifts
        generator.with_user(self.user_admin).write({"state": "confirmed"})
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
            # Verify that reducing end_date is still allowed
            sub.write({"end_date": date(2025, 1, 6)})

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
