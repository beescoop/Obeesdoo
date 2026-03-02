# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import AccessError, UserError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorWritePermissions(
    TestVolunteerGeneratorSubscriptionCommon
):
    """Test write field permissions of shift recurrent generator,
    and subscription management via notebook, depending on generator state and role.

    Note: user group is readonly on generators and subscriptions via access rules.
    """

    def setUp(self):
        super().setUp()

    # Draft generator fields write permissions

    def test_admin_can_write_field_on_draft_generator(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "category_id": self.category_test.id,
            }
        )

    def test_manager_cannot_write_field_on_draft_generator(self):
        with self.assertRaises(AccessError):
            self.gen_today_to_infinite_empty.with_user(self.user_manager).write(
                {
                    "category_id": self.category_test.id,
                }
            )

    # Subscription write permissions for draft generator

    def test_manager_can_write_subscriptions_on_draft_generator(self):
        self.gen_ongoing_with_3_subs.with_user(self.user_manager).write(
            {
                "volunteer_subscription_ids": [
                    Command.update(
                        self.sub_upcoming.id,
                        {
                            "start_date": date(2025, 1, 3),
                            "end_date": date(2025, 1, 4),
                        },
                    )
                ]
            }
        )

    # Confirmed generator fields write permissions

    def test_manager_cannot_write_fields_on_confirmed_generator(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_manager).write(
                {"category_id": self.category_test.id}
            )

    def test_admin_cannot_write_fields_on_confirmed_generator(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
                {"category_id": self.category_test.id}
            )

    # Subscription write permissions for confirmed generator

    def test_manager_can_write_subscriptions_on_confirmed_generator(self):
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.gen_ongoing_with_3_subs.with_user(self.user_manager).write(
            {
                "volunteer_subscription_ids": [
                    Command.update(
                        self.sub_upcoming.id,
                        {
                            "start_date": date(2025, 1, 3),
                            "end_date": date(2025, 1, 4),
                        },
                    )
                ]
            }
        )

    def test_manager_cannot_write_subscriptions_and_write_fields_on_confirmed_generator(
        self,
    ):
        """Test that modifying confirmed generator fields while managing subscription
        is not allowed for manager"""
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_ongoing_with_3_subs.with_user(self.user_manager).write(
                {
                    "category_id": self.category_test.id,
                    "volunteer_subscription_ids": [
                        Command.update(
                            self.sub_upcoming.id,
                            {
                                "start_date": date(2025, 1, 3),
                                "end_date": date(2025, 1, 4),
                            },
                        )
                    ],
                }
            )

    def test_admin_can_write_subscriptions_on_confirmed_generator(self):
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "volunteer_subscription_ids": [
                    Command.update(
                        self.sub_upcoming.id,
                        {
                            "start_date": date(2025, 1, 3),
                            "end_date": date(2025, 1, 4),
                        },
                    )
                ]
            }
        )

    def test_admin_cannot_write_subscriptions_and_fields_on_confirmed_generator(self):
        """Test that modifying confirmed generator fields while managing subscription
        is not allowed for admin"""
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
                {
                    "category_id": self.category_test.id,
                    "volunteer_subscription_ids": [
                        Command.update(
                            self.sub_upcoming.id,
                            {
                                "start_date": date(2025, 1, 3),
                                "end_date": date(2025, 1, 4),
                            },
                        )
                    ],
                }
            )

    # Canceled generator fields write permissions

    def test_manager_cannot_write_fields_on_canceled_generator(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_manager).write(
                {
                    "category_id": self.category_test.id,
                }
            )

    def test_admin_cannot_write_fields_on_canceled_generator(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
                {
                    "category_id": self.category_test.id,
                }
            )

    def test_admin_cannot_write_fields_during_generator_cancellation(self):
        """Test that modifying other fields while setting generator state
        to canceled is not allowed"""
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
                {
                    "state": "canceled",
                    "category_id": self.category_test.id,
                }
            )

    # Write subscription permissions on canceled generator

    def test_manager_cannot_write_subscription_on_canceled_generator(self):
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_ongoing_with_3_subs.with_user(self.user_manager).write(
                {
                    "volunteer_subscription_ids": [
                        Command.update(
                            self.sub_upcoming.id,
                            {
                                "start_date": date(2025, 1, 3),
                                "end_date": date(2025, 1, 4),
                            },
                        )
                    ],
                }
            )

    def test_admin_cannot_write_subscription_on_canceled_generator(self):
        self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_ongoing_with_3_subs.with_user(self.user_admin).write(
                {
                    "volunteer_subscription_ids": [
                        Command.update(
                            self.sub_upcoming.id,
                            {
                                "start_date": date(2025, 1, 3),
                                "end_date": date(2025, 1, 4),
                            },
                        )
                    ],
                }
            )

    # Procedure message to write field of confirmed generator

    def test_admin_gets_procedure_message_on_confirmed_generator_modification(self):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        with self.assertRaisesRegex(UserError, "Duplicate the generator"):
            self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
                {"category_id": self.category_test.id}
            )

    def test_manager_gets_contact_admin_message_on_confirmed_generator_modification(
        self,
    ):
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        with self.assertRaisesRegex(UserError, "Contact your administrator"):
            self.gen_today_to_infinite_empty.with_user(self.user_manager).write(
                {"category_id": self.category_test.id}
            )
