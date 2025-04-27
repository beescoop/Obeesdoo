# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.translate import _


class VolunteerShiftParticipation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # State fields

    registration_state = fields.Selection(
        selection=[("confirmed", "Confirmed"), ("canceled", "Canceled")],
        default="confirmed",
        required=True,
        tracking=True,
    )

    # Date fields

    registration_date = fields.Datetime(tracking=True)
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

    shift_start_time = fields.Datetime(
        string="Start Time", related="shift_id.start_time", store=True, readonly=True
    )

    shift_end_time = fields.Datetime(
        string="End Time", related="shift_id.end_time", store=True, readonly=True
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="shift_id.company_id",
        store=True,
        readonly=True,
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
            # Set registration date to now at creation
            vals["registration_date"] = fields.Datetime.now()
            # Prevent registration to a canceled shift
            shift = self.env["volunteer.shift"].browse(vals.get("shift_id"))
            if shift.state == "canceled":
                raise ValidationError(
                    _("It is not possible to register in a canceled shift.")
                )
            # Set cancellation date to now if the participation is canceled
            if vals.get("registration_state") == "canceled":
                vals["cancellation_date"] = fields.Datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        for participation in self:
            shift = participation.shift_id
            # Restrict uncanceling participation to admins only
            if (
                participation.registration_state == "canceled"
                and vals.get("registration_state") != "canceled"
                and not self.env.context.get("install_mode")
                and not self.env.user.has_group("volunteer.volunteer_group_admin")
            ):
                raise AccessError(
                    _(
                        "Only admins can uncanceled a participation.\n"
                        "You can contact them or create a new participation."
                    )
                )
            # Prevent confirming participation if the shift is canceled
            if (
                shift.state == "canceled"
                and vals.get("registration_state") == "confirmed"
            ):
                raise ValidationError(
                    _(
                        "It is not possible to confirm a participation in a canceled shift."
                    )
                )
            # Set cancellation date to now if the participation is canceled
            else:
                old_state = participation.registration_state
                new_state = vals.get("registration_state")
                if old_state != "canceled" and new_state == "canceled":
                    vals["cancellation_date"] = fields.Datetime.now()
        return super().write(vals)
