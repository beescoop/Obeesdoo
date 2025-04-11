# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

    # State fields

    registration_state = fields.Selection(
        [("confirmed", "Confirmed"), ("canceled", "canceled")],
        default="confirmed",
        required=True,
    )

    # Date fields

    registration_date = fields.Datetime(default=fields.datetime.now(), required=True)
    cancellation_date = fields.Datetime(
        compute="_compute_cancellation_date", store=True
    )

    # Classification fields

    registration_type = fields.Selection(
        [
            ("during_shift", "During-shift"),
            ("manual", "Manual"),
            ("recurrent", "Recurrent"),
            ("website", "Website"),
        ],
        default="manual",
        required=True,
    )

    # Relational fields

    shift_id = fields.Many2one("volunteer.shift", "Shift", required=True)
    volunteer_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)

    # Constraints

    @api.constrains("shift_id", "registration_state")
    def _check_remaining_slots(self):
        for participation in self:
            booking_status = self.shift_id.get_booking_status()
            if not booking_status["can_accept_participation"]:
                nb_confirmed_participation = booking_status[
                    "nb_confirmed_participation"
                ]
                raise ValidationError(
                    _(
                        f"It is not possible to register"
                        f" {nb_confirmed_participation} volunteers in this shift."
                        f" The maximum capacity is {participation.shift_id.max_volunteer_nb}."
                    )
                )

    # Compute Methods

    @api.depends("registration_state")
    def _compute_cancellation_date(self):
        for participation in self:
            if participation.registration_state == "canceled":
                participation.cancellation_date = fields.datetime.now()
            else:
                participation.cancellation_date = False
