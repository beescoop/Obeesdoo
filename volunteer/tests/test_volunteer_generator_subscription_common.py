# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time

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
        self.gen_shift_2_days = self.Generator.create(
            {
                "name": "Generator with 2 days shift",
                "state": "draft",
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2025, 1, 1, 10, 5),
                "end_time": datetime(2025, 1, 2, 12, 5),
                "max_volunteer_nb": 2,
                "type_id": self.type1.id,
            }
        )
        with freeze_time("2024-01-01 01:00:00"):
            self.gen_ongoing_with_3_subs = self.Generator.create(
                {
                    "name": "Ongoing generator with 3 subs",
                    "state": "draft",
                    "until_date": date(2025, 12, 31),
                    "interval_type": "days",
                    "interval": 1,
                    "start_time": datetime(2024, 1, 1, 10, 5),
                    "end_time": datetime(2024, 1, 2, 12, 5),
                    "max_volunteer_nb": 5,
                    "type_id": self.type1.id,
                }
            )

        # Create subscriptions
        # Reference date: 2025-01-01 (globally frozen in test files)
        # - sub_finished: ended before reference date (2024-12)
        # - sub_ongoing: active on reference date (2024-12 ; 2025-12)
        # - sub_upcoming: starts after reference date (2025-02 ; 2025-12)
        with freeze_time("2024-01-01 01:00:00"):
            self.sub_finished = self.Subscription.create(
                {
                    "generator_id": self.gen_ongoing_with_3_subs.id,
                    "volunteer_id": self.volunteer_test.id,
                    "start_date": date(2024, 12, 1),
                    "end_date": date(2024, 12, 31),
                }
            )
            self.sub_ongoing = self.Subscription.create(
                {
                    "generator_id": self.gen_ongoing_with_3_subs.id,
                    "volunteer_id": self.volunteer_confirmed.id,
                    "start_date": date(2024, 12, 1),
                    "end_date": date(2025, 12, 31),
                }
            )
        self.sub_upcoming = self.Subscription.create(
            {
                "generator_id": self.gen_ongoing_with_3_subs.id,
                "volunteer_id": self.volunteer_confirmed2.id,
                "start_date": date(2025, 2, 1),
                "end_date": date(2025, 12, 31),
            }
        )
