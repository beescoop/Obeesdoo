# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class VolunteerCompanyHoliday(models.Model):
    _name = "volunteer.company.holiday"
    _description = "Company Holidays"
    _order = "start_date"

    # Fields

    name = fields.Char(required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        # required=True,
    )

    start_date = fields.Date(required=True)

    end_date = fields.Date(required=True)

    # Methods

    def _cancel_holiday_shift(self, time_in_months=3):
        """Cancel shifts if they cover holiday period within time range"""
        # Forcing admin because of clause in volunteer.volunteer_shift.py
        previous_env = self.env
        self.env = self.env(user=self.env.ref("base.user_admin"))

        # Setting the time range we want to work with
        date_time_range = datetime.today() + relativedelta(months=time_in_months)

        confirmed_future_generated_shifts_in_range = self.env["volunteer.shift"].search(
            [
                ("start_time", ">=", datetime.today()),
                ("start_time", "<=", date_time_range),
                ("generator_id", "!=", None),
                ("state", "=", "confirmed"),
            ]
        )

        # Getting list of shifts to be canceled in case of holidays through generator_id
        potential_shifts_to_cancel = []
        for shift in confirmed_future_generated_shifts_in_range:
            if not shift.generator_id.is_maintained_during_holiday:
                potential_shifts_to_cancel.append(shift)

        future_company_holidays_in_range = self.env["volunteer.company.holiday"].search(
            [
                ("start_date", ">=", date.today()),
                ("start_date", "<=", date_time_range.date()),
            ]
        )

        # Cancel shifts if they're not canceled yet and cover holiday period
        for shift in potential_shifts_to_cancel:
            for holiday in future_company_holidays_in_range:
                if shift.state != "canceled" and self._shift_covers_holiday(
                    shift.start_time,
                    shift.end_time,
                    holiday.start_date,
                    holiday.end_date,
                ):
                    shift.write(
                        {
                            "stage_id": self.env.ref(
                                "volunteer.volunteer_shift_stage_canceled"
                            ).id
                        }
                    )
        # Back to original user
        self.env = previous_env

    def _shift_covers_holiday(
        self, shift_start_time, shift_end_time, holiday_start_date, holiday_end_date
    ):
        """Compare two periods of time, return true if they overlap."""
        shift_start_date = shift_start_time.date()
        shift_end_date = shift_end_time.date()

        if (
            (
                shift_start_date >= holiday_start_date
                and shift_start_date <= holiday_end_date
            )
            or (
                shift_end_date >= holiday_start_date
                and shift_start_date <= holiday_end_date
            )
            or (
                shift_start_date <= holiday_start_date
                and shift_end_date >= holiday_end_date
            )
        ):
            return True
