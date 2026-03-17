# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


# @freeze_time("2026-01-01 10:00:00")
class TestNotificationEndLeave(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        # Force all operations to run as admin
        self.env = self.env(user=self.env.ref("base.user_admin"))

        # Models

        self.Volunteer = self.env["volunteer.volunteer"]
        self.Leave = self.env["volunteer.volunteer.leave"]
        self.VolunteerLeaveType = self.env["volunteer.volunteer.leave.type"]
        self.Company = self.env["res.company"]

        # Records

        # Set number of days before the end of a volunteer's leave
        # to send notification, here 3, for example.
        self.test_company = self.Company.create(
            {
                "name": "LeavingTestCompany",
                "nb_days_before_leave_end": 3,
            }
        )

        # Create necessary leave type.
        self.volunteer_leave_type1 = self.VolunteerLeaveType.create(
            {
                "name": "LeaveTypeTest",
                "description": "Type for autotests",
            }
        )

        self.leaving_volunteer = self.Volunteer.create(
            {
                "name": "LeavingVolunteer",
                "company_id": self.test_company.id,
            }
        )

        self.leaving_volunteer_leave = self.Leave.create(
            {
                "volunteer_id": self.leaving_volunteer.id,
                "type_id": self.volunteer_leave_type1.id,
                "start_date": date(2026, 4, 1),
                "end_date": date(2026, 4, 7),
            }
        )

    def test_send_notification_end_leave(self):
        """Check that a notification is sent to volunteers a certain time
        before the end of their leave."""
        # Check before using the tested method
        # Note that there's already a message sent automatically from OdooBot
        # at creation of volunteer. We thus need to check there is not more than 1 message.
        self.assertEqual(len(self.leaving_volunteer.message_ids), 1)

        # 4 days before end of leave, there shouldn't be any more message yet.
        with freeze_time("2026-04-03 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 1)

        # 3 days before end of leave, a message should be posted.
        with freeze_time("2026-04-04 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 2)

        # 2 days before end of leave, there shouldn't be any more
        # message sent.
        with freeze_time("2026-04-05 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 2)
