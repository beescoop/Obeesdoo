# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from odoo.exceptions import UserError

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorCancellation(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_cannot_create_generator_in_canceled_state(self):
        """Test that creating a generator directly in canceled state is prohibited"""
        with self.assertRaises(UserError):
            self.Generator.create(
                {
                    "name": "GenCanceled",
                    "state": "canceled",
                    "until_date": date(2025, 12, 31),
                    "interval_type": "days",
                    "interval": 1,
                    "start_time": datetime(2024, 1, 1, 10, 5),
                    "end_time": datetime(2024, 1, 1, 12, 5),
                    "tz": "Europe/Brussels",
                    "max_volunteer_nb": 6,
                    "type_id": self.type1.id,
                }
            )

    def test_generator_cancellation_automation(self):
        """Test that canceling a generator cancels future shifts
        and sets subscriptions end_date and until_date generator to today.

        Cancellation strictly applied to future shifts, excluding today,
        independently of time (starting from tomorrow).
        """
        self.gen_with_past_start.write({"state": "confirmed"})
        past_sub = self.Subscription.create(
            {
                "start_date": date(2024, 12, 1),
                "end_date": date(2024, 12, 5),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_with_past_start.id,
            }
        )
        active_sub = self.Subscription.create(
            {
                "start_date": date(2024, 1, 1),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_with_past_start.id,
            }
        )
        future_sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 5),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_with_past_start.id,
            }
        )
        self.gen_with_past_start.write({"state": "canceled"})
        today = date.today()
        future_shifts = self.gen_with_past_start.volunteer_shift_ids.filtered(
            lambda s: s.start_time.date() > today
        )
        self.assertGreater(len(future_shifts), 0)
        for shift in future_shifts:
            self.assertEqual(shift.stage_id, self.stage_canceled)
        self.assertEqual(active_sub.end_date, today)
        self.assertEqual(future_sub.end_date, today)
        self.assertEqual(past_sub.end_date, date(2024, 12, 5))
        self.assertEqual(self.gen_with_past_start.until_date, today)

    def test_generator_cancellation_excludes_today_shifts(self):
        """Test that canceling a generator only cancels shifts starting from tomorrow.
        If there is a shift today, it must remain confirmed.
        """
        self.gen_with_past_start.write({"state": "confirmed"})
        # Advance time to a later date to ensure there is an actual shift generated today.
        with freeze_time("2025-01-04"):
            self.gen_with_past_start.write({"state": "canceled"})
            today = date.today()
            today_shift = self.gen_with_past_start.volunteer_shift_ids.filtered(
                lambda s: s.start_time.date() == today
            )
            self.assertEqual(len(today_shift), 1)
            self.assertEqual(today_shift[0].stage_id, self.stage_confirmed)
