# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class VolunteerShiftRecurrentSubscription(models.Model):
    _name = "volunteer.shift.recurrent.subscription"
    _description = "Shift Recurrent Subscription"
    _order = "start_date"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    start_date = fields.Date()
    end_date = fields.Date()

    # Relational fields

    volunteer_id = fields.Many2one(
        comodel_name="volunteer.volunteer",
        string="Volunteer",
        required=True,
        tracking=True,
    )
    generator_id = fields.Many2one(
        comodel_name="volunteer.shift.recurrent.generator",
        string="Shift Generator",
        required=True,
        tracking=True,
    )

    # Constraints

    @api.constrains("start_date", "end_date")
    def _check_remaining_subscription_slot(self):
        """Ensure there are available subscription slots for the specified period."""
        for subscription in self:
            requested_start_date = subscription.start_date
            requested_end_date = subscription.end_date
            booking_status = subscription.generator_id.get_booking_status(
                requested_start_date, requested_end_date
            )
            if not booking_status["can_accept_subscription"]:
                nb_active_subscriptions = booking_status["nb_active_subscriptions"]
                raise ValidationError(
                    _(
                        f"It is not possible to register"
                        f" {nb_active_subscriptions} volunteers in this generator, "
                        f"for the period {requested_start_date} to {requested_end_date}."
                        f" The maximum capacity is "
                        f"{subscription.generator_id.max_volunteer_nb}."
                    )
                )

    # Override methods

    @api.model_create_multi
    def create(self, vals_list):
        subscriptions = super().create(vals_list)
        for sub in subscriptions:
            sub.generate_participation()
        return subscriptions

    # Methods

    def generate_participation(self):
        """Generate participation for all shifts covered by this subscription"""
        self.ensure_one()
        generator = self.generator_id
        for shift in generator.volunteer_shift_ids:
            if (
                self.start_date <= shift.start_time.date()
                and self.end_date >= shift.end_time.date()
            ):
                existing = self.env["volunteer.shift.participation"].search(
                    [
                        ("shift_id", "=", shift.id),
                        ("volunteer_id", "=", self.volunteer_id.id),
                    ]
                )
                if not existing:
                    self.env["volunteer.shift.participation"].create(
                        {
                            "shift_id": shift.id,
                            "volunteer_id": self.volunteer_id.id,
                            "registration_type": "recurrent",
                            "registration_state": "confirmed",
                        }
                    )
