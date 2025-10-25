# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from .test_volunteer_common import TestVolunteerCommon


class TestVolunteerGeneratorSubscriptionCommon(TestVolunteerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        # Fix number of occurrences for all tests
        self.env.company.shift_nb_occurrence = 10

        # Create recurrent generators
        self.gen_with_past_start = self.Generator.create(
            {
                "name": "GenPastStart",
                "state": "draft",
                "until_date": date(2025, 12, 31),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2024, 1, 1, 10, 5),
                "end_time": datetime(2024, 1, 1, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )
        self.gen_today_to_infinite_empty = self.Generator.create(
            {
                "name": "GenFromTodayToInfiniteWithoutSubscription",
                "state": "draft",
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 1, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )
