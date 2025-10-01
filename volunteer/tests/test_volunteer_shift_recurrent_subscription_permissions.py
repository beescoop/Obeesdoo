# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo.exceptions import AccessError, ValidationError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionPermissions(
    TestVolunteerGeneratorSubscriptionCommon
):
    # Operations run as admin unless another role is explicitly specified.
    # This is defined in setUp() test_volunteer_common.py
    def setUp(self):
        super().setUp()

    def test_create_write_subscription_manager_allowed(self):
        """Test that a user with the 'Volunteer Manager' role can create
        and modify subscriptions on generators in 'draft' and 'confirmed' states."""
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

    def test_create_write_subscription_user_not_allowed(self):
        """Test that a user with the 'Volunteer User' role cannot create
        or write a subscription on any generator state."""
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

    def test_create_write_subscription_canceled_generator_not_allowed(self):
        """Test that creating or writing a subscription on a canceled generator
        is not allowed for any user role, except admins can write end_date to today."""
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
        # User: cannot create or write
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
        # Manager: cannot create or write
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
        # Admin: cannot create, cannot write arbitrary end_date
        with self.assertRaises(ValidationError):
            self.Subscription.with_user(self.user_admin).create(
                {
                    "start_date": date(2025, 1, 6),
                    "end_date": date(2025, 1, 8),
                    "volunteer_id": self.volunteer_test.id,
                    "generator_id": self.gen_without_sub_2025_no_until.id,
                }
            )
        with self.assertRaises(ValidationError):
            sub.with_user(self.user_admin).write(
                {
                    "end_date": date(2025, 1, 4),
                }
            )
        # Admin: CAN write end_date to today (freeze_time: 2025-01-01)
        sub.with_user(self.user_admin).write(
            {
                "end_date": date(2025, 1, 1),
            }
        )
