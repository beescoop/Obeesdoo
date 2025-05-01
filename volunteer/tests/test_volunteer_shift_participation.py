# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import datetime

from freezegun import freeze_time

from odoo.exceptions import AccessError, ValidationError

from .test_volunteer_common import TestVolunteerCommon


class TestVolunteerShiftParticipation(TestVolunteerCommon):
    def setUp(self):
        super().setUp()
        self.now = datetime(2025, 1, 1, 1, 00)

    def test_participation_refused_when_shift_full(self):
        """Test that a participation is refused when the number of confirmed
        participation exceeds max_volunteer_nb"""
        # There is a confirmed participation that is already defined in setUp()
        self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Participation.create(
                {
                    "volunteer_id": self.volunteer_test.id,
                    "shift_id": self.shift_max_2.id,
                    "registration_state": "confirmed",
                }
            )

    def test_set_registration_date(self):
        """Test that the registration date is set to the current date when
        creating a participation"""
        with freeze_time(self.now):
            participation_test = self.Participation.create(
                {
                    "volunteer_id": self.volunteer_confirmed2.id,
                    "shift_id": self.shift_max_2.id,
                    "registration_state": "confirmed",
                }
            )
            self.assertEqual(participation_test.registration_date, self.now)

    def test_set_cancellation_date(self):
        """Test that the cancellation date is set to the current date when
        canceling a participation"""
        with freeze_time(self.now):
            participation_test = self.Participation.create(
                {
                    "volunteer_id": self.volunteer_confirmed2.id,
                    "shift_id": self.shift_max_2.id,
                    "registration_state": "canceled",
                }
            )
            self.assertEqual(participation_test.cancellation_date, self.now)

    def test_confirm_participation_refused_on_shift_canceled(self):
        """Test that a participation is refused when the shift is canceled"""
        shift_canceled = self.Shift.create(
            {
                "name": "Shift Canceled",
                "stage_id": self.stage_canceled.id,
                "start_time": datetime(2025, 12, 24, 10, 5),
                "end_time": datetime(2025, 12, 24, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.Participation.create(
                {
                    "volunteer_id": self.volunteer_canceled.id,
                    "shift_id": shift_canceled.id,
                    "registration_state": "confirmed",
                }
            )

    def test_uncanceled_participation_on_shift_restrict_to_admin(self):
        """Test that only admin can uncanceled a participation"""
        participation_canceled = self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "canceled",
            }
        )
        with self.assertRaises(AccessError):
            participation_canceled.with_user(self.user_user).write(
                {
                    "registration_state": "confirmed",
                }
            )
        with self.assertRaises(AccessError):
            participation_canceled.with_user(self.user_manager).write(
                {
                    "registration_state": "confirmed",
                }
            )
        participation_canceled.with_user(self.user_admin).write(
            {
                "registration_state": "confirmed",
            }
        )
