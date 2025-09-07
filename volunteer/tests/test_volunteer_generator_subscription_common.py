# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from .test_volunteer_common import TestVolunteerCommon


class TestVolunteerGeneratorSubscriptionCommon(TestVolunteerCommon):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

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
        self.gen_with_past_start = self.Generator.create(
            {
                "name": "GenPastStart",
                "state": "draft",
                "until_date": date(2024, 12, 24),
                "interval_type": "days",
                "interval": 1,
                "start_time": datetime(2023, 1, 1, 10, 5),
                "end_time": datetime(2023, 1, 1, 12, 5),
                "tz": "Europe/Brussels",
                "max_volunteer_nb": 6,
                "type_id": self.type1.id,
            }
        )
        self.gen_without_sub_2025_no_until = self.Generator.create(
            {
                "name": "GenWithoutSub2025NoUntil",
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
        # Set up 3 subscriptions with overlapping dates for the same generator
        # with max 3 volunteers
        self.sub_1_to_3 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 3),
                "volunteer_id": self.volunteer_confirmed.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )

        self.sub_2_to_4 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 4),
                "volunteer_id": self.volunteer_confirmed2.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )

        self.sub_3_to_5 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        # Set up 2 subscriptions with overlapping dates for the same generator
        # with max 2 volunteers
        self.sub_2_to_4_test0_max2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 4),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

        self.sub_1_to_5_test1_max2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
