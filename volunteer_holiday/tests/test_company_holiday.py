# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from odoo.tests.common import TransactionCase


class TestCronHoliday(TransactionCase):
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

        self.Holiday = self.env["volunteer.company.holiday"]
        self.Shift = self.env["volunteer.shift"]
        self.Type = self.env["volunteer.shift.type"]
        self.Generator = self.env["volunteer.shift.recurrent.generator"]

        # Stages

        self.stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        self.stage_canceled = self.env.ref("volunteer.volunteer_shift_stage_canceled")

        # Create other company
        self.anoter_company = self.env["res.company"].create({"name": "AnotherCompany"})

        # Create required type
        self.type1 = self.Type.create(
            {
                "name": "TypeTest",
                "description": "Type for autotests",
            }
        )

        # Fix number of occurrences for all tests
        self.env.company.shift_nb_occurrence = 10

        # Create recurrent generators
        self.gen_with_holiday = self.Generator.create(
            {
                "name": "GenWithHoliday",
                "state": "confirmed",
                "until_date": date(2026, 3, 5),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2026, 3, 3, 10, 0),
                "end_time": datetime(2026, 3, 3, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )

        self.gen_without_holiday = self.Generator.create(
            {
                "name": "genWithoutHoliday",
                "state": "confirmed",
                "until_date": date(2026, 3, 2),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2026, 3, 1, 10, 0),
                "end_time": datetime(2026, 3, 1, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )
        self.gen_overlap_holiday = self.Generator.create(
            {
                "name": "genOverlapHoliday",
                "state": "confirmed",
                "until_date": date(2026, 3, 7),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2026, 3, 1, 10, 0),
                "end_time": datetime(2026, 3, 1, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )

        self.gen_long_shift = self.Generator.create(
            {
                "name": "genOverlapHoliday",
                "state": "confirmed",
                "until_date": date(2026, 3, 7),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2026, 3, 1, 10, 0),
                "end_time": datetime(2026, 3, 7, 10, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )

        # Create holidays
        self.march_holiday = self.Holiday.create(
            {
                "name": "marchHolidays",
                # "company_id": self.env.user.company_id,
                "start_date": date(2026, 3, 3),
                "end_date": date(2026, 3, 5),
            }
        )

    def test_cancel_holiday_shift(self):
        """Test that holidays do cancel confirmed generated shifts"""

        # Check before test
        shifts_with_holiday = self.gen_with_holiday.volunteer_shift_ids
        for shift in shifts_with_holiday:
            self.assertEqual(shift.state, "confirmed")

        shifts_without_holiday = self.gen_without_holiday.volunteer_shift_ids
        for shift in shifts_without_holiday:
            self.assertEqual(shift.state, "confirmed")

        shifts_overlap_holiday = self.gen_overlap_holiday.volunteer_shift_ids
        for shift in shifts_overlap_holiday:
            self.assertEqual(shift.state, "confirmed")

        # Call function
        self.Holiday._cancel_holiday_shift()

        # All shifts in shifts_with_holiday cover the march_holidays period,
        # thus should be canceled
        for shift in shifts_with_holiday:
            self.assertEqual(shift.state, "canceled")

        # No shift in shifts_without_holiday cover holiday period,
        # thus shouldn't be canceled
        for shift in shifts_without_holiday:
            self.assertEqual(shift.state, "confirmed")

        # Certain shifts in shifts_overlap_holiday cover holiday period,
        # thus only certain shifts should be canceled
