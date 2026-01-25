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
class TestVolunteerShiftRecurrentSubscriptionWritePermissions(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_cannot_change_volunteer_of_existing_subscription(self):
        """Test that changing the volunteer of an existing subscription is not allowed."""
        # Current volunteer: volunteer_confirmed
        with self.assertRaises(UserError):
            self.sub_ongoing.write({"volunteer_id": self.volunteer_test.id})

    def test_cannot_modify_inactive_subscription(self):
        """Test that inactive subscriptions cannot be modified"""
        self.sub_ongoing.write({"active": False})
        with self.assertRaises(UserError):
            self.sub_ongoing.write({"end_date": date(2025, 1, 15)})
        with self.assertRaises(UserError):
            self.sub_ongoing.write({"start_date": date(2025, 1, 15)})

    def test_cannot_modify_finished_subscription(self):
        """Test that finished subscriptions cannot be modified"""
        with self.assertRaises(UserError):
            self.sub_finished.write({"end_date": date(2025, 1, 15)})
        with self.assertRaises(UserError):
            self.sub_finished.write({"start_date": date(2025, 1, 15)})

    def test_cannot_modify_start_date_of_ongoing_subscription(self):
        """Test that start_date of ongoing subscription cannot be changed"""
        with self.assertRaises(UserError):
            self.sub_ongoing.write({"start_date": date(2025, 1, 1)})

    def test_can_modify_end_date_of_ongoing_subscription(self):
        """Test that end_date of ongoing subscription can be modified"""
        self.sub_ongoing.write({"end_date": date(2025, 1, 10)})

    def test_can_modify_upcoming_subscription(self):
        """Test that upcoming subscriptions are fully modifiable"""
        self.sub_upcoming.write(
            {
                "start_date": date(2025, 1, 10),
                "end_date": date(2025, 1, 31),
            }
        )
