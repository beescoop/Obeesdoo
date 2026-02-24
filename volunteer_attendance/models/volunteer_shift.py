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
        """Compute attendance state according to attendance status
        in all confirmed participations"""
        # Here a function using mapped and filtered doesn't work,
        # as we need to compare a list where every participation is unique
        # with a list where attendance status ids can repeat themselves or
        # be absent. Therefore the use of loops to come out with a custom list
        # and check none values as well as repeated values.
        for shift in self:
            confirmed_participations = shift.volunteer_participation_ids.filtered(
                lambda participation: participation.registration_state == "confirmed"
            )
            all_attendance_status = []
            for participation in confirmed_participations:
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
