# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from odoo.tests import common, new_test_user


class TestVolunteerCommon(common.TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

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
        self.Generator = self.env["volunteer.shift.recurrent.generator"]
        self.Subscription = self.env["volunteer.shift.recurrent.subscription"]

        # Stages
        self.stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        self.stage_canceled = self.env.ref("volunteer.volunteer_shift_stage_canceled")

        # Create test users with different access levels
        self.user_user = new_test_user(
            self.env,
            login="volunteer_user",
            groups="volunteer.volunteer_group_user",
        )
        self.user_manager = new_test_user(
            self.env,
            login="volunteer_manager",
            groups="volunteer.volunteer_group_manager",
        )
        self.user_admin = new_test_user(
            self.env,
            login="volunteer_admin",
            groups="volunteer.volunteer_group_admin",
        )

        # Create required types
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type pour autotests",
            }
        )

        # Create shifts
        self.shift_max_2 = self.Shift.create(
            {
                "name": "Test",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2025, 12, 24, 10, 5),
                "end_time": datetime(2025, 12, 24, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )

        # Create recurrent generators
        self.gen_each_day_max_3_vol = self.Generator.create(
            {
                "name": "GenEachDayMax3",
                "state": "draft",
                "until_date": date(2026, 1, 1),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2024, 1, 1, 10, 5),
                "end_time": datetime(2024, 1, 1, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 3,
                "type_id": self.type1.id,
            }
        )
        self.gen_each_day_max_2_vol = self.Generator.create(
            {
                "name": "GenEachDayMax2",
                "state": "draft",
                "until_date": date(2026, 12, 24),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2024, 1, 1, 10, 5),
                "end_time": datetime(2024, 1, 1, 12, 5),
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

        self.volunteer_test_0 = self.Volunteer.create(
            {
                "name": "VolunteerTest0",
            }
        )
        self.volunteer_test_1 = self.Volunteer.create(
            {
                "name": "VolunteerTest1",
            }
        )
        # Create confirmed participation
        self.participation_confirmed = self.Participation.create(
            {
                "volunteer_id": self.volunteer_confirmed.id,
                "shift_id": self.shift_max_2.id,
                "registration_state": "confirmed",
            }
        )
