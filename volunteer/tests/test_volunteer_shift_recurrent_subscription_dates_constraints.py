# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo.exceptions import UserError, ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionDatesConstraints(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    # Constraint: start_date < end_date

    def test_cannot_create_subscription_with_end_date_before_start_date(self):
        """Test that create subscription with end_date before start_date
        is not allowed."""
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_today_to_infinite_empty.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2025, 2, 1),
                    "end_date": date(2025, 1, 1),
                }
            )

    def test_cannot_write_subscription_with_end_date_before_start_date(self):
        """Test that modifying a subscription with end_date before start_date
        is not allowed."""
        sub = self.Subscription.create(
            {
                "generator_id": self.gen_today_to_infinite_empty.id,
                "volunteer_id": self.volunteer_test.id,
                "start_date": date(2025, 3, 1),
                "end_date": date(2025, 4, 1),
            }
        )
        with self.assertRaises(ValidationError):
            sub.write({"end_date": date(2025, 2, 1)})
        with self.assertRaises(ValidationError):
            sub.write({"start_date": date(2025, 4, 2)})

    def test_cannot_create_subscription_with_same_start_and_end_date(self):
        """Test that subscription with start_date equal to end_date
        is not allowed."""
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_today_to_infinite_empty.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2025, 2, 1),
                    "end_date": date(2025, 2, 1),
                }
            )

    def test_cannot_write_subscription_with_same_start_and_end_date(self):
        """Test that modifying a subscription with start_date
        equal to end_date is not allowed."""
        sub = self.Subscription.create(
            {
                "generator_id": self.gen_today_to_infinite_empty.id,
                "volunteer_id": self.volunteer_test.id,
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 3, 1),
            }
        )
        with self.assertRaises(ValidationError):
            sub.write({"end_date": date(2025, 2, 1)})

    # Constraint: dates not in past

    def test_cannot_create_subscription_with_start_date_in_past(self):
        """Test that create subscription with start_date in the past
        is not allowed."""
        with self.assertRaises(UserError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_today_to_infinite_empty.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2024, 12, 1),
                    "end_date": date(2025, 2, 1),
                }
            )

    def test_cannot_write_end_date_in_past_for_ongoing(self):
        """Test that modifying end_date to past for ongoing subscription
        is not allowed."""
        with self.assertRaises(UserError):
            self.sub_ongoing.write({"end_date": date(2024, 12, 10)})

    def test_cannot_write_dates_in_past_for_upcoming(self):
        """Test that modifying end_date or start_date to past for upcoming subscription
        is not allowed."""
        with self.assertRaises(UserError):
            self.sub_upcoming.write({"start_date": date(2024, 1, 10)})
        with self.assertRaises(UserError):
            self.sub_upcoming.write({"end_date": date(2024, 1, 31)})

    # Constraint: dates within generator period

    def test_cannot_create_subscription_with_start_before_generator_start(self):
        """Test that creating subscription with start_date before
        generator start is not allowed."""
        # Generator start 2025-02-01
        with self.assertRaises(UserError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_with_future_start.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2025, 1, 15),
                    "end_date": date(2025, 3, 1),
                }
            )

    def test_cannot_create_finite_subscription_with_end_beyond_finite_generator_end(
        self,
    ):
        """Test that creating finite subscription with end_date after
        finite generator until_date is not allowed."""
        # Generator until_date 2025-12-31
        with self.assertRaises(UserError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_ongoing_with_3_subs.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2025, 2, 1),
                    "end_date": date(2026, 6, 1),
                }
            )

    def test_cannot_create_infinite_subscription_starting_beyond_finite_generator_end(
        self,
    ):
        """Test that creating infinite subscription starting after
        finite generator until_date is not allowed."""
        # Generator until_date 2025-12-31
        with self.assertRaises(UserError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_ongoing_with_3_subs.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2026, 1, 1),
                }
            )

    def test_can_create_valid_finite_subscription_in_finite_generator(self):
        """Test that creating finite subscription within
        finite generator period is allowed."""
        # Generator start 2024-01-01 until 2025-12-31
        self.Subscription.create(
            {
                "generator_id": self.gen_ongoing_with_3_subs.id,
                "volunteer_id": self.volunteer_test.id,
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 6, 1),
            }
        )

    def test_can_create_valid_infinite_subscription_in_finite_generator(self):
        """Test that creating infinite subscription starting before
        until_date and after start_date of finite generator is allowed."""
        # Generator start 2024-01-01 until 2025-12-31
        self.Subscription.create(
            {
                "generator_id": self.gen_ongoing_with_3_subs.id,
                "volunteer_id": self.volunteer_test.id,
                "start_date": date(2025, 6, 1),
            }
        )

    def test_can_create_valid_finite_subscription_in_infinite_generator(self):
        """Test that creating finite subscription with start_date after
        infinite generator start_date is allowed."""
        # Generator start 2025-01-01
        self.Subscription.create(
            {
                "generator_id": self.gen_today_to_infinite_empty.id,
                "volunteer_id": self.volunteer_test.id,
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 6, 1),
            }
        )
