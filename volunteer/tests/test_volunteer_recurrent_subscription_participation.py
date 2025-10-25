# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentSubscriptionParticipation(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_generate_participation_for_subscription_with_end_date(self):
        """Test that participation are generated only up to the end_date of the subscription
        even if the generator has shift generated beyond the subscription end_date.
        """
        # Generator start_date is 2025/01/01,
        # last shift generated is 2025/01/10 (10 occurrences)
        self.gen_today_to_infinite_empty.write(
            {
                "state": "confirmed",
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 8),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        # Search shifts from 2025-01-06 to 2025-01-08 (3 shifts)
        # which is within subscription dates
        shifts = self.Shift.search(
            [
                ("start_time", ">=", datetime(2025, 1, 6)),
                ("start_time", "<", datetime(2025, 1, 9)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        self.assertEqual(len(shifts), 3)
        parts = self.Participation.search(
            [
                ("shift_id", "in", shifts.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(parts), 3)
        shifts_beyond = self.Shift.search(
            [
                ("start_time", ">=", datetime(2025, 1, 9)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        self.assertEqual(len(shifts_beyond), 2)
        parts_beyond = self.Participation.search(
            [
                ("shift_id", "in", shifts_beyond.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(parts_beyond), 0)

    def test_generate_participation_for_subscription_without_end_date(self):
        """Test that participation are generated for all shifts generated
        when the subscription has no end_date.
        """
        self.gen_today_to_infinite_empty.write(
            {
                "state": "confirmed",
            }
        )
        sub_no_end = self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": False,
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        # Generator start_date is 2025/01/01,
        # last shift generated is 2025/01/10 (10 occurrences)
        shifts = self.Shift.search(
            [
                ("start_time", ">=", sub_no_end.start_date),
                ("start_time", "<", date(2025, 1, 11)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        # From start subscription : 2025-01-06
        # to last date shift generated :2025-01-10
        # there is 5 shifts generated
        self.assertEqual(len(shifts), 5)
        all_participation = self.Participation.search(
            [
                ("shift_id", "in", shifts.ids),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(all_participation), 5)

    def test_autocancel_participation_covered_by_new_subscription_same_volunteer(self):
        """Test that a participation is auto-canceled when a new subscription
        is created that covers the date of the participation for the same volunteer.
        """
        self.gen_today_to_infinite_empty.write(
            {
                "state": "confirmed",
            }
        )
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 7, 10, 5)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        part1 = self.Participation.create(
            {
                "shift_id": shift.id,
                "volunteer_id": self.volunteer_test.id,
                "registration_state": "confirmed",
            }
        )
        self.assertEqual(
            part1.registration_state,
            "confirmed",
        )
        # Create a subscription covering 2025-01-07 for the same volunteer
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 6),
                "end_date": date(2025, 1, 8),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        # Check that punctual participation is auto-canceled
        # and recurrent participation is created,
        # because volunteer is now subscribed for this shift
        self.assertEqual(
            part1.registration_state,
            "canceled",
        )
        recurrent_part = self.Participation.search(
            [
                ("shift_id", "=", shift.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(recurrent_part), 1)
