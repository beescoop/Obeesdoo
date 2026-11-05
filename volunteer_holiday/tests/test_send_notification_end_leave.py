# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date

from freezegun import freeze_time

from .test_volunteer_holiday_common import TestVolunteerHolidayCommon


class TestNotificationEndLeave(TestVolunteerHolidayCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.test_company = self.Company.create(
            {
                "name": "LeavingTestCompany",
                "nb_days_before_leave_end": 3,
            }
        )

        # Create required leave type.
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

        self.leaving_volunteer_leave = self.VolunteerLeave.create(
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
        self.assertEqual(len(self.leaving_volunteer.message_ids), 0)

        # 4 days before end of leave, there shouldn't be any more message yet.
        with freeze_time("2026-04-03 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 0)

        # 3 days before end of leave, a message should be posted.
        with freeze_time("2026-04-04 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 1)

        # 2 days before end of leave, there shouldn't be any more
        # message sent.
        with freeze_time("2026-04-05 10:00:00"):
            self.Volunteer._send_notification_end_leave()
            self.assertEqual(len(self.leaving_volunteer.message_ids), 1)
