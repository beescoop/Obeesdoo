# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.tests import common
from odoo.tools.safe_eval import datetime


class TestVolunteerCommon(common.TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.Shift = self.env["volunteer.shift"]
        self.Type = self.env["volunteer.shift.type"]
        self.Volunteer = self.env["volunteer.volunteer"]
        self.Participation = self.env["volunteer.shift.participation"]

        # Create required type
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type pour autotests",
            }
        )

        # Create shift
        self.shift_max_2 = self.Shift.create(
            {
                "name": "Test",
                "state": "confirmed",
                "start_time": datetime.datetime(2025, 12, 24, 10, 5),
                "end_time": datetime.datetime(2025, 12, 24, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
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
        self.volunteer_test = self.Volunteer.create(
            {
                "name": "VolunteerTest",
            }
        )

        # Create confirmed participation
        self.participationConfirmed = self.env["volunteer.shift.participation"].create(
            {
                "volunteer_id": self.volunteer_confirmed.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
