# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo.exceptions import UserError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionCancellation(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_cancel_subscription_sets_end_date_and_inactive(self):
        """Test that cancelling a subscription sets end_date to today and active to False"""
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        sub.action_cancel_subscription()
        self.assertEqual(sub.end_date, date(2025, 1, 1))
        self.assertFalse(sub.active)

    def test_cannot_cancel_already_canceled_subscription(self):
        """Test that cancelling an already canceled subscription is not allowed"""
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        sub.action_cancel_subscription()
        with self.assertRaises(UserError):
            sub.action_cancel_subscription()
