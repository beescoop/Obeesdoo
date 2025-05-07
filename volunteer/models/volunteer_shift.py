# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.translate import _


class VolunteerShift(models.Model):
    _name = "volunteer.shift"
    _description = "Shift"
    _inherit = ["volunteer.shift.mixin", "mail.thread", "mail.activity.mixin"]

    # General fields

    remaining_slots = fields.Integer(
        compute="_compute_remaining_slots", store=True, tracking=True
    )

    # Stage fields

    @api.model
    def _default_stage_id(self):
        return self.env.ref("volunteer.volunteer_shift_stage_draft")

    stage_id = fields.Many2one(
        comodel_name="volunteer.shift.stage",
        default=_default_stage_id,
        copy=False,
        group_expand="_group_expand_stage_id",
        tracking=True,
    )
    state = fields.Selection(related="stage_id.state", store=True)

    # Relational fields

    volunteer_participation_ids = fields.One2many(
        comodel_name="volunteer.shift.participation",
        inverse_name="shift_id",
        string="Participation",
        tracking=True,
    )
    generator_id = fields.Many2one(
        comodel_name="volunteer.shift.recurrent.generator",
        string="Shift Generator",
        tracking=True,
    )
    volunteer_ids = fields.Many2many(
        comodel_name="volunteer.volunteer",
        compute="_compute_volunteer_ids",
        string="Volunteers",
        store=True,
    )

    _sql_constraints = [
        (
            "shift_max_vol_nb_is_pos",
            "check (max_volunteer_nb > 0)",
            "The maximum of volunteers cannot be null or negative.",
        ),
    ]

    # Compute methods

    @api.depends(
        "volunteer_participation_ids", "volunteer_participation_ids.registration_state"
    )
    def _compute_remaining_slots(self):
        for shift in self:
            nb_confirmed_participation = shift.get_booking_status()[
                "nb_confirmed_participation"
            ]
            shift.remaining_slots = shift.max_volunteer_nb - nb_confirmed_participation

    @api.depends("volunteer_participation_ids")
    def _compute_volunteer_ids(self):
        for shift in self:
            booking_status = shift.get_booking_status()
            if shift.volunteer_participation_ids:
                shift.volunteer_ids = booking_status["confirmed_participation"].mapped(
                    "volunteer_id"
                )
            else:
                shift.volunteer_ids = False

    # Constraints

    @api.constrains("volunteer_participation_ids")
    def _check_unique_volunteer_participation(self):
        """Check that a volunteer can only be registered once per shift."""
        for shift in self:
            confirmed_participation = shift.get_booking_status()[
                "confirmed_participation"
            ]
            confirmed_volunteer_ids = [
                participation.volunteer_id.id
                for participation in confirmed_participation
            ]

            if len(confirmed_volunteer_ids) != len(set(confirmed_volunteer_ids)):
                raise ValidationError(
                    _("A volunteer can only be registered once per shift.")
                )

    @api.constrains("max_volunteer_nb", "volunteer_participation_ids")
    def _check_can_accept_new_participation(self):
        for shift in self:
            booking_status = shift.get_booking_status()
            if not booking_status["can_accept_participation"]:
                nb_confirmed_participation = booking_status[
                    "nb_confirmed_participation"
                ]
                raise ValidationError(
                    _(
                        f"The maximum number of volunteers ({shift.max_volunteer_nb}) "
                        f"cannot be lower than the number "
                        f"of confirmed volunteers ({nb_confirmed_participation})."
                    )
                )

    # Override methods

    def write(self, vals):
        old_states = {shift.id: shift.state for shift in self}
        # Restrict stage change to admins only
        if (
            "stage_id" in vals
            and not self.env.context.get("install_mode")
            and not self.env.user.has_group("volunteer.volunteer_group_admin")
        ):
            raise AccessError(_("Only admins can change the state of a shift"))
        res = super().write(vals)
        for shift in self:
            previous_state = old_states[shift.id]
            # Auto-cancel confirmed participation if the shift is canceled
            if previous_state != "canceled" and shift.state == "canceled":
                confirmed_participation = shift.get_booking_status()[
                    "confirmed_participation"
                ]
                confirmed_participation.write({"registration_state": "canceled"})
        return res

    # Methods

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    def get_booking_status(self):
        """Get the shift booking status by returning a dictionary of :
        - can_accept_participation: boolean
        - confirmed_participation: recordset of confirmed participation
        - nb_confirmed_participation: number of confirmed participation
        """
        self.ensure_one()
        confirmed_participation = self.volunteer_participation_ids.filtered(
            lambda participation: participation.registration_state == "confirmed"
        )
        nb_confirmed_participation = len(confirmed_participation)
        booking_status = {
            "can_accept_participation": True,
            "confirmed_participation": confirmed_participation,
            "nb_confirmed_participation": nb_confirmed_participation,
        }
        if self.max_volunteer_nb < nb_confirmed_participation:
            booking_status["can_accept_participation"] = False
        return booking_status
