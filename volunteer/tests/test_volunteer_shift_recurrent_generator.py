# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date, datetime

from odoo.exceptions import ValidationError

from .test_volunteer_common import TestVolunteerCommon


class TestVolunteerShiftRecurrentGenerator(TestVolunteerCommon):
    def setUp(self):
        super().setUp()

        # Set up 3 subscriptions with overlapping dates for the same generator
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
        self.sub_2_to_4_test0_max2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 2),
                "end_date": date(2025, 1, 4),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

        self.sub_1_to_5_test1_max_2 = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

    def test_subscription_exceed_max_3_with_overlaps(self):
        # There is already 3 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2024, 12, 3),
                    "end_date": date(2025, 1, 10),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )

    def test_subscription_exceed_max_3_with_overlaps_borders(self):
        # There is already 3 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 1),
                    "end_date": date(2025, 1, 3),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 3),
                    "end_date": date(2025, 1, 5),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_3_vol.id,
                }
            )

    def test_subscription_exceed_max_2_one_single_day(self):
        # There is already 2 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteer
        # 01/03 : 2 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 2),
                    "end_date": date(2025, 1, 2),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_2_vol.id,
                }
            )

    def test_subscription_without_overlaps_dont_exceed_max_3(self):
        # There is already 3 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )

    def test_write_extend_subscription_causes_exceeding_max(self):
        # There is already 3 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        new_sub = self.Subscription.create(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        with self.assertRaises(ValidationError):
            new_sub.write(
                {
                    "end_date": date(2025, 1, 5),
                }
            )

    def test_unsubscribe_allows_new_subscription(self):
        # There is already 2 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteer
        # 01/03 : 2 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        with self.assertRaises(ValidationError):
            self.Subscription.create(
                {
                    "start_date": date(2025, 1, 3),
                    "end_date": date(2025, 1, 3),
                    "volunteer_id": self.volunteer_canceled.id,
                    "generator_id": self.gen_each_day_max_2_vol.id,
                }
            )
        self.sub_1_to_5_test1_max_2.write(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 1),
                "volunteer_id": self.volunteer_test_1.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 3),
                "end_date": date(2025, 1, 3),
                "volunteer_id": self.volunteer_canceled.id,
                "generator_id": self.gen_each_day_max_2_vol.id,
            }
        )

    def test_autocancel_participation_covered_by_new_sub_same_volunteer(self):
        # There is already 3 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteers
        # 01/03 : 3 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        self.gen_each_day_max_3_vol.with_user(self.user_admin).write(
            {
                "state": "confirmed",
            }
        )
        shift = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 2, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_3_vol.id),
            ]
        )
        shift_id = shift.id
        participation = self.Participation.create(
            {
                "shift_id": shift_id,
                "volunteer_id": self.volunteer_test_0.id,
                "registration_state": "confirmed",
            }
        )
        sub = self.Subscription.create(
            {
                "start_date": date(2024, 1, 1),
                "end_date": date(2024, 1, 2),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        sub.write(
            {
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 1, 2),
            }
        )
        shift2 = self.Shift.search(
            [
                ("start_time", "=", datetime(2025, 1, 4, 10, 5)),
                ("generator_id", "=", self.gen_each_day_max_3_vol.id),
            ]
        )
        shift2_id = shift2.id
        part2 = self.Participation.create(
            {
                "shift_id": shift2_id,
                "volunteer_id": self.volunteer_test_0.id,
                "registration_state": "confirmed",
            }
        )
        self.Subscription.create(
            {
                "start_date": date(2025, 1, 4),
                "end_date": date(2025, 1, 5),
                "volunteer_id": self.volunteer_test_0.id,
                "generator_id": self.gen_each_day_max_3_vol.id,
            }
        )
        self.assertEqual(
            participation.registration_state,
            "canceled",
        )
        self.assertEqual(
            part2.registration_state,
            "canceled",
        )

    def test_reduce_max_volunteer_under_nb_subscription(self):
        # There is already 2 subscriptions created in setUp() for january 1 to 5:
        # 01/01 : 1 volunteer
        # 01/02 : 2 volunteer
        # 01/03 : 2 volunteers
        # 01/04 : 2 volunteers
        # 01/05 : 1 volunteer
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "max_volunteer_nb": 1,
                }
            )

    # Note : Limitation is not yet implemented - currently allows modification
    # in any state
    # def test_modification_on_confirmed_generator_not_allowed(self):
    #     # It is not possible to modify until_date, period and max_volunteer
    #     # on confirmed generator
    #     self.gen_each_day_max_2_vol.write(
    #         {
    #             "until_date": date(2026, 1, 1),
    #         }
    #     )
    #
    #     self.gen_each_day_max_2_vol.write(
    #         {
    #             "start_time": datetime(2025, 1, 1, 13, 0),
    #         }
    #     )
    #     self.gen_each_day_max_2_vol.write(
    #         {
    #             "end_time": datetime(2025, 1, 1, 13, 0),
    #         }
    #     )
    #     self.gen_each_day_max_2_vol.write(
    #         {
    #             "max_volunteer_nb": 3,
    #         }
    #     )
    #     self.gen_each_day_max_2_vol.with_user(self.user_admin).write(
    #         {
    #             "state": "confirmed",
    #         }
    #     )
    #     with self.assertRaises(ValidationError):
    #         self.gen_each_day_max_2_vol.write(
    #             {
    #                 "max_volunteer_nb": 4,
    #             }
    #         )
    #     with self.assertRaises(ValidationError):
    #         self.gen_each_day_max_2_vol.write(
    #             {
    #                 "until_date": date(2026, 1, 3),
    #             }
    #         )
    #     with self.assertRaises(ValidationError):
    #         self.gen_each_day_max_2_vol.write(
    #             {
    #                 "start_time": datetime(2025, 1, 1, 15, 0),
    #             }
    #         )
    #     with self.assertRaises(ValidationError):
    #         self.gen_each_day_max_2_vol.write(
    #             {
    #                 "end_time": datetime(2025, 1, 1, 16, 0),
    #             }
    #         )
