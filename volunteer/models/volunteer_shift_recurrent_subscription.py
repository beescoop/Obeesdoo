# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class VolunteerShiftRecurrentSubscription(models.Model):
    _name = "volunteer.shift.recurrent.subscription"
    _description = "Shift Recurrent Subscription"
    _order = "start_date"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    # Date fields

    start_date = fields.Date(
        required=True, tracking=True, default=lambda self: fields.Date.today()
    )
    end_date = fields.Date(tracking=True)

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

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="generator_id.company_id",
        store=True,
        readonly=True,
    )

    # Override methods

    @api.model_create_multi
    def create(self, vals_list):
        subscriptions = super().create(vals_list)
        for sub in subscriptions:
            if sub.generator_id.state == "confirmed":
                sub.generate_participation()
        return subscriptions

    # Methods

    def generate_participation(self):
        """Generate participation for all future shifts covered by this subscription.
        This method cancels any conflicting punctual participation before generating
        the recurrent participation.
        """
        self.ensure_one()
        future_shifts = self._get_future_shifts_in_subscription_period()
        self._cancel_conflicting_punctual_participation(future_shifts)
        self._generate_participation_by_shifts(future_shifts)

    def _get_future_shifts_in_subscription_period(self):
        """Get all future shifts in the period defined by this subscription."""
        self.ensure_one()
        today = fields.Date.today()
        shifts = self.generator_id.volunteer_shift_ids.filtered(
            lambda shift: shift.start_time.date() >= today
            and shift.start_time.date() >= self.start_date
        )
        if self.end_date:
            shifts = shifts.filtered(
                lambda shift: shift.end_time.date() <= self.end_date
            )
        return shifts

    def _generate_participation_by_shifts(self, shifts):
        """Generate participation records for the given shifts
        for the volunteer linked to this subscription.
        """
        self.ensure_one()
        participation_to_create = []
        for shift in shifts:
            participation_to_create.append(
                {
                    "shift_id": shift.id,
                    "volunteer_id": self.volunteer_id.id,
                    "registration_type": "recurrent",
                    "registration_state": "confirmed",
                }
            )
        self.env["volunteer.shift.participation"].create(participation_to_create)

    def _cancel_conflicting_punctual_participation(self, shifts):
        """Cancel the punctual participation of a volunteer if they subscribe
        for a period when they already have punctual participation registered.
        """
        self.ensure_one()
        all_participation_to_cancel = self.env["volunteer.shift.participation"].search(
            [
                ("shift_id", "in", shifts.ids),
                ("volunteer_id", "=", self.volunteer_id.id),
                ("registration_state", "=", "confirmed"),
                ("registration_type", "!=", "recurrent"),
            ]
        )
        if all_participation_to_cancel:
            all_participation_to_cancel.write(
                {
                    "registration_state": "canceled",
                }
            )
