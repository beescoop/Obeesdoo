# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class VolunteerShiftParticipation(models.Model):
    _inherit = ["volunteer.shift.participation"]

    attendance_status_id = fields.Many2one(
        comodel_name="volunteer.shift.attendance.status",
        string="Attendance Status",
    )
    attendance_date = fields.Datetime()

    # Constraints

    @api.constrains("attendance_status_id")
    def _check_no_attendance_status_for_canceled_participation(self):
        for participation in self:
            if (
                participation.registration_state == "canceled"
                and participation.attendance_status_id is not None
            ):
                raise ValidationError(
                    _(
                        "An attendance status for a canceled participation "
                        "will not be taken into account for the attendance state "
                        "of the shift."
                    )
                )

    # Methods

    @api.depends("attendance_status_id")
    def write(self, vals):
        """Set attendance status modification date to now at modification"""
        vals["attendance_date"] = fields.Datetime.now()
        return super().write(vals)
