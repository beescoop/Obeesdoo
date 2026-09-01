# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from odoo.tests.common import TransactionCase


class TestVolunteerHolidayCommon(TransactionCase):
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
        self.Holiday = self.env["volunteer.company.holiday"]
        self.Company = self.env["res.company"]
        self.VolunteerLeave = self.env["volunteer.volunteer.leave"]
        self.VolunteerLeaveType = self.env["volunteer.volunteer.leave.type"]

        # Recurrent records

        self.anoter_company = self.Company.create({"name": "AnotherCompany"})

        # Mandatory records to use for required fields in other recs

        self.stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        self.stage_canceled = self.env.ref("volunteer.volunteer_shift_stage_canceled")
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
