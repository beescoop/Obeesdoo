# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from odoo import api, fields, models


class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    overlaps_holiday = fields.Boolean(
        string="Overlaps with Company Holidays",
        compute="_compute_overlap_holiday",
        tracking=True,
        store=True,
    )

    @api.depends("start_time", "end_time", "company_id")
    def _compute_overlap_holiday(self):
        """Compute if shift overlaps with any company holiday period."""
        date_today = datetime.today().date()
        Holiday = self.env["volunteer.company.holiday"]
        future_shifts = self.env["volunteer.shift"].search(
            [("end_time", ">=", datetime.today())]
        )
        for shift in future_shifts:
            found_overlap = False
            this_company_future_holidays = self.env["volunteer.company.holiday"].search(
                [
                    ("end_date", ">=", date_today),
                    ("company_id", "=", shift.company_id.id),
                ]
            )
            for holiday in this_company_future_holidays:
                if Holiday._shift_covers_holiday(
                    shift.start_time,
                    shift.end_time,
                    holiday.start_date,
                    holiday.end_date,
                ):
                    found_overlap = True
                    shift.overlaps_holiday = True

            if not found_overlap:
                shift.overlaps_holiday = False
