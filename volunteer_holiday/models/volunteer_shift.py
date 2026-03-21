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

    # # This field needs more thinking. See method below.
    # overlapping_holiday_ids = fields.Many2many(
    #     comodel_name="volunteer.company.holiday",
    #     string="Overlap with: ",
    #     compute="_compute_overlap_holiday",
    #     store=True,
    # )

    @api.depends("start_time", "end_time", "company_id")
    def _compute_overlap_holiday(self):
        """Compute if shift overlaps with any company holiday period."""
        # # For now, this function only applies to future shifts and holidays.
        # # Some thinking will be needed regarding the update of the fields
        # # overlapping_holiday_ids and overlaps_holiday over time, and whether
        # # changing dates in the past should be possible or not.
        date_today = datetime.today().date()
        Holiday = self.env["volunteer.company.holiday"]
        future_shifts = self.env["volunteer.shift"].search(
            [("end_time", ">=", datetime.today())]
        )
        for shift in future_shifts:
            # old_overlapping_holidays = shift.overlapping_holiday_ids
            # new_overlapping_holidays = []
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
                    # new_overlapping_holidays.extend(holiday)
                    # shift.overlapping_holiday_ids += holiday.id

            if not found_overlap:
                shift.overlaps_holiday = False

            # # Can't get to write this with proper syntax for now. Considering this
            # # is only one side of the function, as there needs to be another one to do
            # # the same job in volunteer.company.holiday.

            # elif old_overlapping_holidays != new_overlapping_holidays:
            #     old_and_new = list(set(old_overlapping_holidays + new_overlapping_holidays))
            #     for holiday in old_and_new:
            #         if (holiday in old_overlapping_holidays
            #           and holiday not in new_overlapping_holidays):
            #             shift.write({"overlapping_holiday_ids": [(3, holiday.id)]})
            #         elif (holiday in new_overlapping_holidays
            #           and holiday not in old_overlapping_holidays):
            #             shift.write({"overlapping_holiday_ids": [(4, holiday.id)]})

            # print(shift.overlapping_holiday_ids)
