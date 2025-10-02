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

    # Note : Constraints managed by SQL constraints produce Odoo logs
    # which need to be muted to avoid polluting tests outputs.
    # Savepoints are used to prevent the transaction from being blocked
    # when a SQL exception (e.g. CheckViolation) is raised.
    def test_reduce_max_volunteer_equals_zero_not_allowed(self):
        """Test that it is not possible to reduce max_volunteer_nb to 0"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_without_sub_2025_no_until.write(
                        {
                            "max_volunteer_nb": 0,
                        }
                    )

    def test_reduce_nb_occurrence_equals_zero_not_allowed(self):
        """Test that it is not possible to reduce nb_occurrence to 0"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_without_sub_2025_no_until.write(
                        {
                            "nb_occurrence": 0,
                        }
                    )

    def test_reduce_interval_equals_zero_not_allowed(self):
        """Test that it is not possible to reduce interval to 0"""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.gen_each_day_max_2_vol.write(
                        {
                            "interval": 0,
                        }
                    )

    def test_reduce_max_volunteer_nb_under_nb_actives_subscriptions_not_allowed(self):
        """Test that reducing max_volunteer_nb under the max number of existing
        subscriptions is not allowed"""
        # Setup creates 2 overlapping subscriptions (max 2 on same day)
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write(
                {
                    "max_volunteer_nb": 1,
                }
            )

    def test_create_write_until_date_before_start_date_not_allowed(self):
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
            # Start_date is 2024-01-01
            with self.assertRaises(ValidationError):
                self.gen_each_day_max_2_vol.write(
                    {
                        "until_date": date(2023, 12, 24),
                    }
                )

    def test_write_until_date_under_existing_subscription_not_allowed(self):
        """Test that modifying until_date is not allowed
        if there are subscriptions after the new until_date"""
        # Start_date generator : 2024-01-01
        # Until_date generator : 2026-12-24
        # There are subscriptions in 2025
        # Setting until_date to False should be allowed
        self.gen_each_day_max_2_vol.write({"until_date": False})
        # Reducing until_date to 2024 is not allowed
        # since there are subscriptions in 2025
        with self.assertRaises(ValidationError):
            self.gen_each_day_max_2_vol.write({"until_date": date(2024, 1, 1)})

    def test_create_subscription_from_notebook_same_volunteer_with_overlap_not_allowed(
        self,
    ):
        """Test that creating a subscription for the same volunteer
        at the same period from generator notebook is not allowed"""
        # Setup has no subscriptions after 2025-01-05
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
