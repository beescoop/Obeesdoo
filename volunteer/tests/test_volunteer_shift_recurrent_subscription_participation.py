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
        # last shift generated is 2025/01/11 (10 occurrences, starting from 2025-01-02)
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
        self.assertEqual(len(shifts_beyond), 3)
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

    def _check_existing_recurrent_participation_state_for_days(
        self, generator, volunteer, days, state
    ):
        """Helper to check the state of volunteer's participation
        for given generator and iterable days.
        """
        for day in days:
            shift = self.Shift.search(
                [
                    ("start_time", "=", datetime(2025, 1, day, 10, 5)),
                    ("generator_id", "=", generator.id),
                ],
                limit=1,
            )
            self.assertTrue(shift)
            part = self.Participation.search(
                [
                    ("shift_id", "=", shift.id),
                    ("volunteer_id", "=", volunteer.id),
                    ("registration_type", "=", "recurrent"),
                    ("registration_state", "=", state),
                ]
            )
            self.assertEqual(len(part), 1)

    def test_reducing_subscription_creates_no_duplicate_participation(self):
        """Test that reducing subscription end_date modifies participation state
        without creating duplicate records.
        """
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
        shift_9 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 9, 10, 5)),
                ("generator_id", "=", self.gen_today_to_infinite_empty.id),
            ]
        )
        # Check initial state
        part_9_before_write = self.Participation.search(
            [
                ("shift_id", "=", shift_9.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part_9_before_write), 1)
        # Reduce end date to 2025-01-08
        # needs to cancel participation on 2025-01-09
        sub.write({"end_date": date(2025, 1, 8)})
        part_9_after_write = self.Participation.search(
            [
                ("shift_id", "=", shift_9.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
            ]
        )
        # Check that participation for shift on 2025-01-09 is canceled
        # and there is no other participation for this shift and volunteer
        self.assertEqual(len(part_9_after_write), 1)
        self.assertEqual(part_9_after_write.id, part_9_before_write.id)
        self.assertEqual(part_9_after_write.registration_state, "canceled")

    def test_extending_subscription_to_infinite(self):
        """Test that extending subscription to infinite generates participation
        for all generated shifts."""
        self.gen_today_to_infinite_empty.with_user(self.user_admin).write(
            {"state": "confirmed"}
        )
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_today_to_infinite_empty.id,
            }
        )
        sub.write({"end_date": False})
        self._check_existing_recurrent_participation_state_for_days(
            self.gen_today_to_infinite_empty,
            self.volunteer_test,
            range(2, 11),
            "confirmed",
        )

    def _run_intersection_test(self, generator):
        """Helper to test intersection handling when modifying subscription.

        Scenario:
            Initial subscription: 2025-01-02 to 2025-01-06
            Modified subscription: 2025-01-04 to 2025-01-08

        Expected behavior:
            - Intersection period (01-04 to 01-06): participation stay confirmed
            - New period (01-07 to 01-08): participation are generated
            - Old period (01-02 to 01-03): participation are canceled
        """
        generator.with_user(self.user_admin).write({"state": "confirmed"})
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": generator.id,
            }
        )
        # Move subscription from 01-02 to 01-06 to 01-04 to 01-08
        # which creates an intersection between old and new subscription periods
        # on 01-04 to 01-06
        sub.write({"start_date": date(2025, 1, 4), "end_date": date(2025, 1, 8)})

        # Intersection (01-04 to 01-06) needs to stay unchanged (confirmed)
        self._check_existing_recurrent_participation_state_for_days(
            generator,
            self.volunteer_test,
            range(4, 7),
            "confirmed",
        )
        # New period outside intersection (01-07 to 01-08) needs to be generated
        self._check_existing_recurrent_participation_state_for_days(
            generator,
            self.volunteer_test,
            range(7, 9),
            "confirmed",
        )
        # Old period outside intersection (01-02 to 01-03) needs to be canceled
        self._check_existing_recurrent_participation_state_for_days(
            generator,
            self.volunteer_test,
            range(2, 4),
            "canceled",
        )

    def test_managing_cancel_create_participation_intersection_single_day(self):
        """Test intersection handling with single-day shifts."""
        self._run_intersection_test(self.gen_today_to_infinite_empty)

    def test_managing_cancel_create_participation_intersection_multi_day(self):
        """Test intersection handling with multi-day shifts."""
        self._run_intersection_test(self.gen_shift_2_days)

    def _run_no_intersection_test(self, generator):
        """Helper to test full replacement when modifying subscription.

        Scenario:
            Initial subscription: 2025-01-02 to 2025-01-06
            Modified subscription: 2025-01-07 to 2025-01-10

        Expected behavior:
            - New period (01-07 to 01-10): participation are generated
            - Old period (01-02 to 01-06): participation are canceled
        """
        generator.with_user(self.user_admin).write({"state": "confirmed"})
        sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 6),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": generator.id,
            }
        )
        # Full replacement (no intersection) of the subscription
        # from 01-02 to 01-06 to 01-07 to 01-10
        sub.write({"start_date": date(2025, 1, 7), "end_date": date(2025, 1, 10)})
        # New period needs to be generated (01-07 to 01-10)
        self._check_existing_recurrent_participation_state_for_days(
            generator,
            self.volunteer_test,
            range(7, 11),
            "confirmed",
        )
        # Old period needs to be canceled (01-02 to 01-06)
        self._check_existing_recurrent_participation_state_for_days(
            generator,
            self.volunteer_test,
            range(2, 7),
            "canceled",
        )

    def test_managing_cancel_create_participation_no_intersection_single_day(self):
        """Test full replacement with single-day shifts."""
        self._run_no_intersection_test(self.gen_today_to_infinite_empty)

    def test_managing_cancel_create_participation_no_intersection_multi_day(self):
        """Test full replacement with multi-day shifts."""
        self._run_no_intersection_test(self.gen_shift_2_days)

    def test_multi_day_shift_generation(self):
        """Test that participation for multi-day shifts are generated when the subscription
        stops on first day of the shift, without covering the end of the shift on other day.

        Example:
            Shift multiday (2025-01-02 to 2025-01-03), subscription starts 2025-01-02,
            should generate participation for the shift of 2025-01-02,
            even if the shift extends beyond this day (2025-01-03).
        """
        self.gen_shift_2_days.with_user(self.user_admin).write({"state": "confirmed"})
        # Create a subscription ending on the same day as the start of the shift
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_shift_2_days.id,
            }
        )
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 2, 10, 5)),
                ("generator_id", "=", self.gen_shift_2_days.id),
            ],
            limit=1,
        )
        self.assertTrue(shift)
        self.assertNotEqual(shift.start_time.date(), shift.end_time.date())
        part = self.Participation.search(
            [
                ("shift_id", "=", shift.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part), 1)

    def test_subscription_starts_after_first_day_of_multiday_shift(self):
        """Test that a subscription starting after the first day of a multi-day shift
        does not create participation (shift started before subscription).

        Example:
            Shift multiday (2025-01-02 to 2025-01-03), subscription starts 2025-01-03,
            should not have participation for the shift of 2025-01-02.
        """
        self.gen_shift_2_days.with_user(self.user_admin).write({"state": "confirmed"})
        # Subscription starts on the end day of shift 01-03
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": date(2025, 1, 10),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_shift_2_days.id,
            }
        )
        # No participation should be created on 01-02
        # (shift started before subscription)
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 2, 10, 5)),
                ("generator_id", "=", self.gen_shift_2_days.id),
            ],
            limit=1,
        )
        self.assertTrue(shift)
        part = self.Participation.search(
            [
                ("shift_id", "=", shift.id),
                ("volunteer_id", "=", self.volunteer_test.id),
                ("registration_type", "=", "recurrent"),
                ("registration_state", "=", "confirmed"),
            ]
        )
        self.assertEqual(len(part), 0)
        # Participation should exist for shifts starting from 01-03
        self._check_existing_recurrent_participation_state_for_days(
            self.gen_shift_2_days,
            self.volunteer_test,
            range(3, 11),
            "confirmed",
        )
