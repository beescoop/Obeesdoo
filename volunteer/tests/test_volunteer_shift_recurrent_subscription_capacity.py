# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionCapacity(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

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

    def test_create_multiple_sub_different_volunteers_capacity_exceeded(self):
        """Test that creating multiple subscriptions for different volunteers
        that would exceed the max_volunteer_nb for any day in the subscription
        period is not allowed."""
        # There is already 2 subscriptions created in setUp() only for 2025 january 1 to 5
        # Tested subscriptions don't overlap with these setUp data (20-24 january)
        vals_list_capacity_exceeded = [
            {
                "start_date": date(2025, 1, 20),
                "end_date": date(2025, 1, 22),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
            {
                "start_date": date(2025, 1, 21),
                "end_date": date(2025, 1, 23),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
            {
                "start_date": date(2025, 1, 22),
                "end_date": date(2025, 1, 24),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            },
        ]
        with self.assertRaises(ValidationError):
            self.Subscription.create(vals_list_capacity_exceeded)

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
