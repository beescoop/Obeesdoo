# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_holiday_common import TestVolunteerHolidayCommon


@freeze_time("2026-01-01 10:00:00")
class TestCompanyHoliday(TestVolunteerHolidayCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.Generator = self.env["volunteer.shift.recurrent.generator"]

        # Fix number of occurrences for all tests
        self.env.company.shift_nb_occurrence = 10

        # Create recurrent generators
        self.gen_with_holiday = self.Generator.create(
            {
                "name": "GenWithHoliday",
                "state": "confirmed",
                "is_maintained_during_holiday": False,
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

        self.gen_maintained_during_holiday = self.Generator.create(
            {
                "name": "GenMaintainedDuringHoliday",
                "state": "confirmed",
                "is_maintained_during_holiday": True,
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
                "is_maintained_during_holiday": False,
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

        self.gen_one_long_shift = self.Generator.create(
            {
                "name": "genOneLongShift",
                "state": "confirmed",
                "is_maintained_during_holiday": False,
                "until_date": date(2026, 3, 8),
                "interval_type": "months",
                "interval": 1,
                "start_time": datetime(2026, 3, 1, 10, 0),
                "end_time": datetime(2026, 3, 7, 10, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )

        self.gen_overlap_holiday = self.Generator.create(
            {
                "name": "genOverlapHoliday",
                "state": "confirmed",
                "is_maintained_during_holiday": False,
                "until_date": date(2026, 3, 6),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2026, 3, 2, 10, 0),
                "end_time": datetime(2026, 3, 2, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )

        # Create holidays
        self.march_holiday = self.Holiday.create(
            {
                "name": "marchHolidays",
                "start_date": date(2026, 3, 3),
                "end_date": date(2026, 3, 5),
            }
        )

    def test_cancel_holiday_shift(self):
        """Test that holidays do cancel confirmed generated shifts"""

        # Checks before test
        shifts_on_holiday = self.gen_with_holiday.volunteer_shift_ids
        for shift in shifts_on_holiday:
            self.assertEqual(shift.state, "confirmed")

        maintained_shifts = self.gen_maintained_during_holiday.volunteer_shift_ids
        for shift in maintained_shifts:
            self.assertEqual(shift.state, "confirmed")

        shifts_without_holiday = self.gen_without_holiday.volunteer_shift_ids
        for shift in shifts_without_holiday:
            self.assertEqual(shift.state, "confirmed")

        one_long_shift = self.gen_one_long_shift.volunteer_shift_ids
        for shift in one_long_shift:
            self.assertEqual(shift.state, "confirmed")

        # Here generator overlapping with holiday period
        shifts_overlap_holiday = self.gen_overlap_holiday.volunteer_shift_ids
        for shift in shifts_overlap_holiday:
            self.assertEqual(shift.state, "confirmed")

        # Call function
        self.Holiday._cancel_holiday_shift()

        # All shifts in shifts_on_holiday cover the march_holidays period,
        # thus should be canceled
        for shift in shifts_on_holiday:
            self.assertEqual(shift.state, "canceled")

        # Maintained shifts shouldn't be canceled
        for shift in maintained_shifts:
            self.assertEqual(shift.state, "confirmed")

        # No shift in shifts_without_holiday covers holiday period,
        # thus shouldn't be canceled
        for shift in shifts_without_holiday:
            self.assertEqual(shift.state, "confirmed")

        # This long shift should be canceled entirely as it overlaps with holiday period
        for shift in one_long_shift:
            self.assertEqual(shift.state, "canceled")

        # Overlapping shifts should be canceled, the others should stay
        for shift in shifts_overlap_holiday:
            # Holidays last from 3/3/26 to 5/3/2026
            if shift.start_time == datetime(2026, 3, 2, 10, 0):
                self.assertEqual(shift.state, "confirmed")
            if shift.start_time == datetime(2026, 3, 3, 10, 0):
                self.assertEqual(shift.state, "canceled")
            if shift.start_time == datetime(2026, 3, 4, 10, 0):
                self.assertEqual(shift.state, "canceled")
            if shift.start_time == datetime(2026, 3, 5, 10, 0):
                self.assertEqual(shift.state, "canceled")
            if shift.start_time == datetime(2026, 3, 6, 10, 0):
                self.assertEqual(shift.state, "confirmed")

        # Create holidays of another company
        self.other_company_holiday = self.Holiday.sudo().create(
            {
                "name": "marchOtherHolidays",
                "company_id": self.anoter_company.id,
                "start_date": date(2026, 3, 6),
                "end_date": date(2026, 3, 6),
            }
        )

        # Call function again
        self.Holiday._cancel_holiday_shift()

        # Check that shift of March 6 wasn't canceled,
        # as March 6 holiday is registered for a different company
        # than March 6 shift
        march_6_shift = shifts_overlap_holiday.filtered(
            lambda shift: shift.start_time == datetime(2026, 3, 6, 10, 0)
        )
        self.assertEqual(march_6_shift.state, "confirmed")
