# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import date, datetime

from odoo import fields, models


class VolunteerVolunteerLeave(models.Model):
    _name = "volunteer.volunteer.leave"
    _description = "Volunteer Leave"
    _order = "start_date desc, volunteer_id, id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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

    # Methods

    def _cancel_volunteer_leave_participation(self):
        """Cancel participations of volunteers if they overlap with their time off"""
        Holiday = self.env["volunteer.company.holiday"]
        today_midnight = datetime.today().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        all_future_volunteer_leaves = self.search([("end_date", ">=", date.today())])

        for leave in all_future_volunteer_leaves:
            future_confirmed_participations = (
                leave.volunteer_id.shift_participation_ids.filtered(
                    lambda participation: participation.registration_state != "canceled"
                    and participation.shift_id.state != "canceled"
                    and participation.shift_id.start_time >= today_midnight
                )
            )
            for participation in future_confirmed_participations:
                if Holiday._shift_covers_holiday(
                    participation.shift_id.start_time,
                    participation.shift_id.end_time,
                    leave.start_date,
                    leave.end_date,
                ):
                    participation.write({"registration_state": "canceled"})
