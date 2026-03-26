# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime
from itertools import groupby

from odoo import api, fields, models


class VolunteerCompanyHoliday(models.Model):
    _name = "volunteer.company.holiday"
    _description = "Company Holidays"
    _order = "start_date"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Fields

    name = fields.Char(required=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    start_date = fields.Date(required=True, tracking=True)

    end_date = fields.Date(required=True, tracking=True)

    # SQL Constraints

    _sql_constraints = [
        (
            "start_d_smaller_than_end_d",
            "CHECK (start_date <= end_date)",
            "Start date shouldn't be greater than end date.",
        ),
    ]

    # Override Methods

    def write(self, vals):
        result = super().write(vals)
        if "start_date" in vals or "end_date" in vals:
            self.env["volunteer.shift"]._compute_overlap_holiday()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        if "start_date" in vals_list or "end_date" in vals_list:
            self.env["volunteer.shift"]._compute_overlap_holiday()
        return result

    def unlink(self):
        result = super().unlink()
        self.env["volunteer.shift"]._compute_overlap_holiday()
        return result

    # Methods

    def _cancel_holiday_shift(self):
        """Cancel shifts if they cover holiday period within time range."""
        today_midnight = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        future_company_holidays = self.env["volunteer.company.holiday"].search(
            [("start_date", ">=", today_midnight)],
            order="company_id",
        )

        for company_id, grouped_holidays_by_company in groupby(
            future_company_holidays, key=lambda holiday: holiday.company_id
        ):
            same_company_shifts = self.env["volunteer.shift"].search(
                [
                    ("company_id", "=", company_id.id),
                    ("state", "=", "confirmed"),
                    ("start_time", ">=", today_midnight),
                    ("generator_id", "!=", False),
                    ("generator_id.is_maintained_during_holiday", "=", False),
                ]
            )
            for hol in grouped_holidays_by_company:
                for shift in same_company_shifts:
                    if self._shift_covers_holiday(
                        shift.start_time,
                        shift.end_time,
                        hol.start_date,
                        hol.end_date,
                    ):
                        shift.write(
                            {
                                "stage_id": self.env.ref(
                                    "volunteer.volunteer_shift_stage_canceled"
                                ).id,
                            }
                        )

    # Helper method

    @api.model
    def _shift_covers_holiday(
        self, shift_start_time, shift_end_time, holiday_start_date, holiday_end_date
    ):
        """Compare two periods of time, return true if they overlap."""
        shift_start_date = shift_start_time.date()
        shift_end_date = shift_end_time.date()

        return (
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
        )
