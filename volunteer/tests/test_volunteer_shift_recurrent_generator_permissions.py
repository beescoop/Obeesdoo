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
class TestVolunteerShiftRecurrentGeneratorPermissions(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

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
