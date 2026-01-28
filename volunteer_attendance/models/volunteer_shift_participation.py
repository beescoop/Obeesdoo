# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class VolunteerShiftParticipation(models.Model):
    _inherit = ["volunteer.shift.participation"]
    # Couldn't add ["mail.thread", "mail.activity.mixin"] to _inherit, raises error.

    attendance_status_id = fields.Many2one(
        comodel_name="volunteer.shift.attendance.status",
        string="Attendance Status",
        tracking=True,
    )

    attendance_date = fields.Datetime(tracking=True)

    @api.depends("attendance_status_id")
    def write(self, vals):
        # Set attendance status modification date to now at modification
        vals["attendance_date"] = fields.Datetime.now()
        return super().write(vals)
