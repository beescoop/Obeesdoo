# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later


from odoo import api, fields, models


class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    overlaps_holiday = fields.Boolean(
        string="Overlaps with Company Holidays",
        compute="_compute_overlap_holiday",
        tracking=True,
        store=True,
    )

    # Compute Method

    @api.depends("start_time", "end_time", "company_id")
    def _compute_overlap_holiday(self):
        """Compute if shift overlaps with any company holiday period."""
        Holiday = self.env["volunteer.company.holiday"]
        for shift in self:
            # Setting local variable
            found_overlap = False
            company_holidays = self.env["volunteer.company.holiday"].search(
                [
                    ("company_id", "=", shift.company_id.id),
                ],
            )
            for hol in company_holidays:
                if Holiday._shift_covers_holiday(
                    shift.start_time,
                    shift.end_time,
                    hol.start_date,
                    hol.end_date,
                ):
                    found_overlap = True
                    break

            shift.overlaps_holiday = found_overlap
