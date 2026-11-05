# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_holiday_common import TestVolunteerHolidayCommon


@freeze_time("2026-01-01 10:00:00")
class TestVolunteerShift(TestVolunteerHolidayCommon):
    def setUp(self):
        super().setUp()

        # Records

        self.easter_holiday = self.Holiday.create(
            {
                "name": "Easter",
                "start_date": date(2026, 4, 6),
                "end_date": date(2026, 4, 6),
            }
        )

        self.shift_no_overlap = self.Shift.create(
            {
                "name": "ShiftNoOverlap",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 4, 5, 10, 0),
                "end_time": datetime(2026, 4, 5, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )

        self.shift_overlap = self.Shift.create(
            {
                "name": "ShiftOverlap",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 4, 6, 10, 0),
                "end_time": datetime(2026, 4, 6, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )

        self.shift_other_company = self.Shift.create(
            {
                "name": "ShiftOtherCompany",
                "stage_id": self.stage_confirmed.id,
                "start_time": datetime(2026, 4, 6, 10, 0),
                "end_time": datetime(2026, 4, 6, 12, 0),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
                "company_id": self.anoter_company.id,
            }
        )

    def test_compute_overlap_holiday(self):
        """Test that overlaps_holiday does change according
        current shifts and holidays"""
        # The compute_overlap_holiday is triggered when holidays are
        # created, written or unlinked, as well as when start_time
        # and end_time are modificated in shifts.
        self.assertFalse(self.shift_no_overlap.overlaps_holiday)
        self.assertTrue(self.shift_overlap.overlaps_holiday)
        self.assertFalse(self.shift_other_company.overlaps_holiday)
