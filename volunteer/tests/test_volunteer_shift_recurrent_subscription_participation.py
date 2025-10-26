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

    def test_autocancel_participation_covered_by_modified_sub_same_volunteer(self):
        """Test that a participation is auto-canceled when an existing subscription
        is modified to cover the date of the participation for the same volunteer."""
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 8, 10, 5)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        part = self.Participation.create(
            {
                "shift_id": shift.id,
                "volunteer_id": self.volunteer_test.id,
                "registration_state": "confirmed",
            }
        )
        self.assertEqual(
            part.registration_state,
            "confirmed",
        )
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 4),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        # Extend subscription to infinite to cover participation date
        sub.write(
            {
                "end_date": False,
            }
        )
        self.assertEqual(
            part.registration_state,
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

    def test_managing_cancel_or_create_participation(self):
        """Test managing canceling or creating participation when modifying
        a subscription end_date including setting it to None (no end)."""
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 7),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        shift_8 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 8, 10, 5)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        part_8_confirmed = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_8_confirmed), 1)
        # Reduce end date to 2025-01-07
        # needs to cancel participation on 2025-01-08
        sub.write({"end_date": date(2025, 1, 7)})
        part_8_canceled = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "canceled"),
            ]
        )
        # Check that participation for shift on 2025-01-08 is canceled
        # and there is no other confirmed participation for this shift
        # and volunteer
        self.assertEqual(len(part_8_canceled), 1)
        part_8 = self.Participation.search(
            [
                ("shift_id", "=", shift_8.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_8), 0)
        # Modify end date to False (infinite)
        # needs to create participation after 2025-01-08 (check 2025-01-10)
        sub.write({"end_date": False})
        shift_10 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 10, 10, 5)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        part_10 = self.Participation.search(
            [
                ("shift_id", "=", shift_10.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_10), 1)
