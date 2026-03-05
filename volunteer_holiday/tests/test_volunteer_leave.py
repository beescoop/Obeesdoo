# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


@freeze_time("2026-03-01 10:00:00")
class TestVolunteerLeave(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        # Force all operations to run as admin
        self.env = self.env(user=self.env.ref("base.user_admin"))

        # Set up the environment
        self.env = self.env(
            context=dict(
                self.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )

        # Models

        self.Volunteer = self.env["volunteer.volunteer"]
        self.Shift = self.env["volunteer.shift"]
        self.Type = self.env["volunteer.shift.type"]
        self.VolunteerLeave = self.env["volunteer.volunteer.leave"]
        self.VolunteerLeaveType = self.env["volunteer.volunteer.leave.type"]
        self.Participation = self.env["volunteer.shift.participation"]

        # Create required stages
        self.stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        self.stage_canceled = self.env.ref("volunteer.volunteer_shift_stage_canceled")

        # Create required types
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type for autotests",
            }
        )
        self.volunteer_leave_type1 = self.VolunteerLeaveType.create(
            {
                "name": "LeaveTypeTest",
                "description": "Type for autotests",
            }
        )

        # Create shifts
        self.shift1 = self.Shift.create(
            {
                "name": "Shift1",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 4, 1, 10, 5),
                "end_time": datetime(2026, 4, 1, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        self.shift2 = self.Shift.create(
            {
                "name": "Shift2",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 4, 2, 10, 5),
                "end_time": datetime(2026, 4, 2, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )

        # Create volunteers, one that has time off, one that doesn't
        self.leaving_volunteer = self.Volunteer.create({"name": "LeavingVolunteer"})
        self.staying_volunteer = self.Volunteer.create({"name": "StayingVolunteer"})

        # Create confirmed participations
        self.leaving_volunteer_participation1 = self.Participation.create(
            {
                "volunteer_id": self.leaving_volunteer.id,
                "shift_id": self.shift1.id,
                "registration_state": "confirmed",
            }
        )
        self.leaving_volunteer_participation2 = self.Participation.create(
            {
                "volunteer_id": self.leaving_volunteer.id,
                "shift_id": self.shift2.id,
                "registration_state": "confirmed",
            }
        )
        self.staying_volunteer_participation1 = self.Participation.create(
            {
                "volunteer_id": self.staying_volunteer.id,
                "shift_id": self.shift1.id,
                "registration_state": "confirmed",
            }
        )
        self.staying_volunteer_participation2 = self.Participation.create(
            {
                "volunteer_id": self.staying_volunteer.id,
                "shift_id": self.shift2.id,
                "registration_state": "confirmed",
            }
        )

        # Create leaves for leaving volunteer
        self.leaving_volunteer_leave = self.VolunteerLeave.create(
            {
                "volunteer_id": self.leaving_volunteer.id,
                "type_id": self.volunteer_leave_type1.id,
                "start_date": date(2026, 4, 1),
                "end_date": date(2026, 4, 2),
            }
        )

    def test_cancel_volunteer_leave_participation(self):
        """Test that volunteer participations are canceled
        if the associated shifts overlap with the volunteer's time off"""

        # Checks before test
        self.assertEqual(
            self.leaving_volunteer_participation1.registration_state, "confirmed"
        )
        self.assertEqual(
            self.leaving_volunteer_participation2.registration_state, "confirmed"
        )
        self.assertEqual(
            self.staying_volunteer_participation1.registration_state, "confirmed"
        )
        self.assertEqual(
            self.staying_volunteer_participation2.registration_state, "confirmed"
        )

        # Call function
        self.VolunteerLeave._cancel_volunteer_leave_participation()

        # Participations of the leaving volunteer should be canceled
        self.assertEqual(
            self.leaving_volunteer_participation1.registration_state, "canceled"
        )
        self.assertEqual(
            self.leaving_volunteer_participation2.registration_state, "canceled"
        )
        # Participations of the staying volunteer should be confirmed
        self.assertEqual(
            self.staying_volunteer_participation1.registration_state, "confirmed"
        )
        self.assertEqual(
            self.staying_volunteer_participation2.registration_state, "confirmed"
        )
