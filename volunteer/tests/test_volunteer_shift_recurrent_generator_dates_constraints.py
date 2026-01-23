# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from freezegun import freeze_time
from psycopg2.errors import CheckViolation

from odoo.tools import mute_logger

from .test_volunteer_generator_subscription_common import (
    TestVolunteerGeneratorSubscriptionCommon,
)


@freeze_time("2025-01-01 10:00:00")
class TestVolunteerShiftRecurrentGeneratorDatesConstraints(
    TestVolunteerGeneratorSubscriptionCommon
):
    def setUp(self):
        super().setUp()

    def test_cannot_create_generator_with_end_time_before_start_time(self):
        """Test that create generator with end_time before start_time
        is not allowed."""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    self.Generator.create(
                        {
                            "name": "GenInvalid",
                            "state": "draft",
                            "until_date": date(2025, 3, 1),
                            "interval_type": "days",
                            "interval": 1,
                            "start_time": datetime(2025, 1, 1, 12, 6),
                            "end_time": datetime(2025, 1, 1, 12, 5),
                            "tz": "Europe/Brussels",
                            "max_volunteer_nb": 3,
                            "type_id": self.type1.id,
                        }
                    )

    def test_cannot_write_generator_with_end_time_before_start_time(self):
        """Test that modifying a draft generator with end_time before start_time
        is not allowed."""
        with mute_logger("odoo.sql_db"):
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    # Start time is 2025-01-01 10:05
                    self.gen_today_to_infinite_empty.write(
                        {"end_time": datetime(2025, 1, 1, 10, 4)}
                    )
            with self.assertRaises(CheckViolation):
                with self.cr.savepoint():
                    # End time is 2025-01-01 12:05
                    self.gen_today_to_infinite_empty.write(
                        {
                            "start_time": datetime(2025, 1, 1, 12, 6),
                        }
                    )
