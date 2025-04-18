# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # State fields

    registration_state = fields.Selection(
        selection=[("confirmed", "Confirmed"), ("canceled", "canceled")],
        default="confirmed",
        required=True,
        tracking=True,
    )

    # Date fields

    registration_date = fields.Datetime(default=fields.datetime.now(), required=True)
    cancellation_date = fields.Datetime(tracking=True)

    # Classification fields

    registration_type = fields.Selection(
        selection=[
            ("during_shift", "During-shift"),
            ("manual", "Manual"),
            ("recurrent", "Recurrent"),
            ("website", "Website"),
        ],
        default="manual",
        required=True,
        tracking=True,
    )

    # Relational fields

    shift_id = fields.Many2one(
        comodel_name="volunteer.shift", string="Shift", required=True, tracking=True
    )
    volunteer_id = fields.Many2one(
        comodel_name="volunteer.volunteer",
        string="Volunteer",
        required=True,
        tracking=True,
    )

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

    # Override methods

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("registration_state") == "canceled":
                vals["cancellation_date"] = fields.datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        for participation in self:
            old_state = participation.registration_state
            new_state = vals.get("registration_state")
            if old_state != "canceled" and new_state == "canceled":
                vals["cancellation_date"] = fields.datetime.now()
        return super().write(vals)
