# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from odoo import api, fields, models


class VolunteerVolunteerLeave(models.Model):
    _name = "volunteer.volunteer.leave"
    _description = "Volunteer Leave"
    _order = "start_date"

    # Relational Fields

    volunteer_id = fields.Many2one(
        comodel_name="volunteer.volunteer",
        string="Volunteer",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="volunteer_id.company_id",
    )
    type_id = fields.Many2one(
        comodel_name="volunteer.volunteer.leave.type",
        string="Leave Type",
        required="True",
    )

    # Time fields

    start_date = fields.Date(
        required=True,
    )
    end_date = fields.Date(
        required=True,
    )

    # Methods

    def _cancel_volunteer_leave_participation(self):
        """Cancel participations of volunteers if they overlap with their time off"""
        today_midnight = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        all_future_volunteer_leaves = (
            self.env["volunteer.volunteer.leave"]
            .sudo()
            .search([("start_date", ">=", date.today())])
        )

        for leave in all_future_volunteer_leaves:
            future_confirmed_participations = (
                leave.volunteer_id.shift_participation_ids.filtered(
                    lambda participation: participation.registration_state != "canceled"
                    and participation.shift_id.state != "canceled"
                    and participation.shift_id.start_time >= today_midnight
                )
            )
            for participation in future_confirmed_participations:
                if self._shift_covers_holiday(
                    participation.shift_id.start_time,
                    participation.shift_id.end_time,
                    leave.start_date,
                    leave.end_date,
                ):
                    participation.sudo().write({"registration_state": "canceled"})

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
