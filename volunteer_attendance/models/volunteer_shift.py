# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    attendance_state = fields.Selection(
        selection=[("waiting", "Waiting"), ("validated", "Validated")],
        help="Validated if every volunteer is given an attendance status.",
        compute="_compute_attendance_state",
        store=True,
    )

    # Methods

    @api.depends("volunteer_participation_ids.attendance_status_id")
    def _compute_attendance_state(self):
        for shift in self:
            all_attendance_status = []
            for participation in shift.volunteer_participation_ids:
                all_attendance_status.append(participation.attendance_status_id.name)
            if all(all_attendance_status):
                shift.attendance_state = "validated"
            else:
                shift.attendance_state = "waiting"

    def action_display_attendance_state(self):
        """Display participations with no attendance status"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Participations",
            "res_model": "volunteer.shift.participation",
            "view_mode": "tree",
            "domain": [
                ("shift_id", "=", [self.id]),
                ("attendance_status_id", "=", None),
            ],
        }
