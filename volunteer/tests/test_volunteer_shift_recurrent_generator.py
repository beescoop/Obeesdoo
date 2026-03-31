# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGenerator(TestVolunteerGeneratorSubscriptionCommon):
    def setUp(self):
        super().setUp()

    def test_search_volunteer_name_by_states(self):
        """Test _search_volunteer_name_by_states() via ongoing_volunteer_name search field."""
        with freeze_time("2024-01-01 01:00:00"):
            gen_with_one_ongoing_sub = self.Generator.create(
                {
                    "name": "GenWithOneOngoingSub",
                    "state": "draft",
                    "interval_type": "days",
                    "interval": 1,
                    "start_time": datetime(2024, 1, 1, 10, 5),
                    "end_time": datetime(2024, 1, 1, 12, 5),
                    "tz": "Europe/Brussels",
                    "max_volunteer_nb": 6,
                    "type_id": self.type1.id,
                }
            )
            self.Subscription.create(
                {
                    "generator_id": gen_with_one_ongoing_sub.id,
                    "volunteer_id": self.volunteer_confirmed.id,
                    "start_date": date(2024, 12, 1),
                    "end_date": date(2025, 12, 31),
                }
            )
        matching_search_result = self.Generator.search(
            [("ongoing_volunteer_name", "ilike", self.volunteer_confirmed.name)]
        )
        self.assertIn(gen_with_one_ongoing_sub, matching_search_result)
        unmatched_search_result = self.Generator.search(
            [("ongoing_volunteer_name", "ilike", self.volunteer_confirmed2.name)]
        )
        self.assertNotIn(gen_with_one_ongoing_sub, unmatched_search_result)
