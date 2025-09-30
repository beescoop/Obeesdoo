# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time
from psycopg2.errors import CheckViolation

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


# Freeze time to past date to prevent errors when
# testing subscriptions with past start dates
@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorConstraints(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_reduce_max_volunteer_equals_zero(self):
        """Test that it is not possible to reduce max_volunteer_nb to 0"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_without_sub_2025_no_until.write(
                        {
                            "max_volunteer_nb": 0,
                        }
                    )

    def test_reduce_nb_occurrence_equals_zero(self):
        """Test that it is not possible to reduce nb_occurrence to 0"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_without_sub_2025_no_until.write(
                        {
                            "nb_occurrence": 0,
                        }
                    )

    def test_interval_equals_zero(self):
        """Test that modifying a generator with
        interval equal to 0 is not allowed"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_each_day_max_2_vol.write(
                        {
                            "interval": 0,
                        }
                    )

    def test_reduce_max_volunteer_under_nb_subscription(self):
        """Test that reducing max_volunteer_nb under the max number of existing
        subscriptions is not allowed"""
        # Setup creates 2 overlapping subscriptions (max 2 on same day)
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "max_volunteer_nb": 1,
                }
            )

    def test_until_date_before_start_date_not_allowed(self):
        """Test that creating or modifying a generator with
        until_date before start_date is not allowed"""
        with self.subTest("Create generator with until_date before start_date"):
            with self.assertRaises(ValidationError):
                self.Generator.create(
                    {
                        "name": "GenInvalid",
                        "state": "draft",
                        "until_date": date(2023, 12, 24),
                        "interval_type": "days",
                        "interval": 1,
                        "start_time": datetime(2024, 1, 1, 10, 5),
                        "end_time": datetime(2024, 1, 1, 12, 5),
                        "tz": "Europe/Brussels",
                        "max_volunteer_nb": 3,
                        "type_id": self.type1.id,
                    }
                )
        with self.subTest("Modify generator to have until_date before start_date"):
            # Start_date is 2024/1/1
            with self.assertRaises(ValidationError):
                self.gen_each_day_max_2_vol.write(
                    {
                        "until_date": date(2023, 12, 24),
                    }
                )

    def test_modify_until_date(self):
        """Test that modifying until_date is not allowed
        if there are subscriptions after the new until_date"""
        # Start_date generator : 2024/1/1
        # Until_date generator : 2026/12/24
        # There are subscriptions in 2025
        self.gen_each_day_max_2_vol.write({"until_date": False})
        # Reducing until_date to 2024 should be rejected
        # since there are subscriptions in 2025
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write({"until_date": date(2024, 1, 1)})

    def test_subscription_for_the_same_volunteer_at_the_same_period_not_allowed(self):
        """Test that creating a subscription for the same volunteer
        at the same period is not allowed"""
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "volunteer_subscription_ids": [
                        Command.create(
                            {
                                "start_date": date(2025, 1, 6),
                                "end_date": date(2025, 1, 8),
                                "volunteer_id": self.volunteer_test_0.id,
                            }
                        ),
                        Command.create(
                            {
                                "start_date": date(2025, 1, 7),
                                "end_date": date(2025, 1, 9),
                                "volunteer_id": self.volunteer_test_0.id,
                            }
                        ),
                    ]
                }
            )
