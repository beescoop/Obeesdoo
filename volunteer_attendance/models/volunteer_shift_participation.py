# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftParticipation(models.Model):
    _inherit = "volunteer.shift.participation"

    attendance_status_id = fields.Many2one(
        comodel_name="volunteer.shift.attendance.status",
        string="Attendance Status",
        tracking=True,
    )
