# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from odoo.tests import common


class TestVolunteerShiftAttendance(common.TransactionCase):
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
        self.Shift = self.env["volunteer.shift"]
        self.Type = self.env["volunteer.shift.type"]
        self.Volunteer = self.env["volunteer.volunteer"]
        self.Participation = self.env["volunteer.shift.participation"]
        self.AttendanceStatus = self.env["volunteer.shift.attendance.status"]

        # Stages
        self.stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        self.stage_canceled = self.env.ref("volunteer.volunteer_shift_stage_canceled")

        # Create required types
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type for autotests",
            }
        )

        # Create attendance status
        self.attendance_status_test = self.AttendanceStatus.create(
            {
                "name": "TestAttendanceStatus",
            }
        )

        # Create shift
        self.standard_shift = self.Shift.create(
            {
                "name": "StandardShift",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 3, 1, 8, 0, 0),
                "end_time": datetime(2026, 3, 1, 10, 0, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 5,
                "type_id": self.type1.id,
            }
        )

        # Create volunteers
        self.volunteer_confirmed = self.Volunteer.create(
            {
                "name": "VolunteerConfirmed",
            }
        )
        self.volunteer_confirmed2 = self.Volunteer.create(
            {
                "name": "VolunteerConfirmed2",
            }
        )
        self.volunteer_canceled = self.Volunteer.create(
            {
                "name": "VolunteerCanceled",
            }
        )

        # Create confirmed participation
        self.participation_confirmed = self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed.id,
                "shift_id": self.standard_shift.id,
                "registration_state": "confirmed",
                "attendance_status_id": self.attendance_status_test.id,
            }
        )
        self.participation_confirmed2 = self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed2.id,
                "shift_id": self.standard_shift.id,
                "registration_state": "confirmed",
                "attendance_status_id": self.attendance_status_test.id,
            }
        )
        self.participation_canceled = self.Participation.create(
            {
                "volunteer_id": self.volunteer_canceled.id,
                "shift_id": self.standard_shift.id,
                "registration_state": "canceled",
            }
        )

    def test_01_compute_attendance_state(self):
        """Test that attendance state is correctly computed"""
        self.assertEqual("waiting", self.standard_shift.attendance_state)
        self.participation_canceled.attendance_status_id = (
            self.attendance_status_test.id
        )
        self.assertEqual("validated", self.standard_shift.attendance_state)
