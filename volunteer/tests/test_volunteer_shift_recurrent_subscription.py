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
class TestVolunteerShiftRecurrentSubscription(TestVolunteerGeneratorSubscriptionCommon):
    def setUp(self):
        super().setUp()

    def test_temporal_state_upcoming(self):
        """Test that subscription with future start_date is upcoming"""
        self.assertEqual(self.sub_upcoming.temporal_state, "upcoming")

    def test_temporal_state_ongoing(self):
        """Test that subscription with past start and future end is ongoing"""
        self.assertEqual(self.sub_ongoing.temporal_state, "ongoing")

    def test_temporal_state_finished(self):
        """Test that subscription with past end_date is finished"""
        self.assertEqual(self.sub_finished.temporal_state, "finished")

    def test_create_inactive_subscription_is_not_allowed(self):
        """Test that creating an inactive subscription is not allowed"""
        with self.assertRaises(UserError):
            self.Subscription.create(
                {
                    "generator_id": self.gen_today_to_infinite_empty.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2025, 1, 1),
                    "end_date": date(2025, 2, 1),
                    "active": False,
                }
            )
