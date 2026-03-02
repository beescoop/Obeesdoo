# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from freezegun import freeze_time

from odoo.exceptions import UserError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorStateChangePermissions(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_manager_cannot_write_generator_state(self):
        """Test that manager cannot change the state of a generator."""
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.with_user(self.user_manager).write(
                {
                    "state": "confirmed",
                }
            )

    def test_cannot_go_back_to_draft_state_from_confirmed(self):
        """Test it is not possible to go back to draft state for generator,
        from confirmed state."""
        self.gen_today_to_infinite_empty.write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.write(
                {
                    "state": "draft",
                }
            )

    def test_cannot_go_back_to_draft_state_from_canceled(self):
        """Test it is not possible to go back to draft state for generator
        from canceled state."""
        self.gen_today_to_infinite_empty.write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.write(
                {
                    "state": "draft",
                }
            )

    def test_cannot_change_state_of_canceled_generator(self):
        """Test it is not possible to change the state of a canceled generator."""
        self.gen_today_to_infinite_empty.write(
            {
                "state": "canceled",
            }
        )
        with self.assertRaises(UserError):
            self.gen_today_to_infinite_empty.write(
                {
                    "state": "confirmed",
                }
            )
