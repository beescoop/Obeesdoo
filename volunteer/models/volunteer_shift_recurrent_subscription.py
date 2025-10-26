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

    def write(self, vals):
        old_sub_data = {}
        for sub in self:
            old_sub_data[sub.id] = {
                "start_date": sub.start_date,
                "end_date": sub.end_date,
                "generator_id": sub.generator_id.id,
                "volunteer_id": sub.volunteer_id.id,
            }
        res = super().write(vals)
        for sub in self:
            old_sub = old_sub_data.get(sub.id)
            sub._managing_cancel_or_create_participation(
                old_sub.get("start_date"), old_sub.get("end_date")
            )
        return res

    # Methods

    def _get_shifts_intersection_between_two_periods(
        self, new_start_date, new_end_date, old_start_date, old_end_date
    ):
        """Get all shifts in the intersection between two periods."""
        self.ensure_one()
        intersection_start_date = max(new_start_date, old_start_date)
        intersection_end_date = min(new_end_date, old_end_date)
        if intersection_start_date > intersection_end_date:
            # No intersection
            return []
        shifts_intersection = self.generator_id.volunteer_shift_ids.filtered(
            lambda shift: shift.start_time.date() >= intersection_start_date
            and shift.end_time.date() <= intersection_end_date
        )
        return shifts_intersection

    def generate_participation(self):
        """Generate participation for all future shifts covered by this subscription.
        This method cancels any conflicting punctual participation before generating
        the recurrent participation.
        """
        self.ensure_one()
        future_shifts = self._get_future_shifts_in_subscription_period()
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
        self._cancel_conflicting_punctual_participation(shifts)
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

    def _cancel_participation_by_shifts(self, shifts):
        """Cancel all participation for given shifts
        for the volunteer concerned by subscription in self.
        """
        self.ensure_one()
        for shift in shifts:
            participation_to_cancel = self.env["volunteer.shift.participation"].search(
                [
                    ("shift_id", "=", shift.id),
                    ("volunteer_id", "=", self.volunteer_id.id),
                    ("registration_state", "=", "confirmed"),
                ]
            )
            if participation_to_cancel:
                participation_to_cancel.write(
                    {
                        "registration_state": "canceled",
                    }
                )

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

    def _managing_cancel_or_create_participation(self, old_start_date, old_end_date):
        """Manage the cancellation and generation of participation for the adequate periods.

        The intersection between old and new subscription is an unchanged period.
        New subscription areas outside of the intersection need participation to be generated.
        Old subscription areas outside of the intersection need participation to be canceled.

        Special case: if there is no intersection, all old participation need to be canceled
        and new ones need to be generated.

        Note: Cases of exact match between new and old subscriptions are not processed
        since they mean there is no change requested.
        """
        self.ensure_one()
        future_shifts = self.generator_id._get_future_shifts()
        if not future_shifts:
            return
        new_end_date = self.end_date
        new_start_date = self.start_date
        date_last_shift = future_shifts.sorted("end_time", reverse=True)[
            0
        ].end_time.date()
        if not new_end_date:
            new_end_date = date_last_shift
        if not old_end_date:
            old_end_date = date_last_shift
        shifts_intersection = self._get_shifts_intersection_between_two_periods(
            new_start_date, new_end_date, old_start_date, old_end_date
        )
        if not shifts_intersection:
            # No intersection : all old shifts need to be canceled
            old_shifts = future_shifts.filtered(
                lambda shift: shift.start_time.date() >= old_start_date
                and shift.end_time.date() <= old_end_date
            )
            self._cancel_participation_by_shifts(old_shifts)
            # All shifts covered by the new subscription need to be generated
            # Call generate_participation on self, which is up to date
            # since this management method is called after super().write()
            self.generate_participation()
        else:
            # Define the boundaries of the full period between old and new subscription
            start_date_full_period = min(new_start_date, old_start_date)
            end_date_full_period = max(new_end_date, old_end_date)
            # Filter the full period excluding the intersection period
            shifts_full_period_without_intersection = future_shifts.filtered(
                lambda shift: shift.start_time.date() >= start_date_full_period
                and shift.end_time.date() <= end_date_full_period
                and shift.id not in shifts_intersection.ids
            )
            # Filter the period of new subscription without intersection and in the full range
            shifts_new_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: shift.start_time.date() >= new_start_date
                and shift.end_time.date() <= new_end_date
            )
            # Generate participation for shifts newly covered by the subscription
            self._generate_participation_by_shifts(shifts_new_sub_only)
            # Filter the period of old subscription without intersection and in the full range
            shifts_old_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: shift.start_time.date() >= old_start_date
                and shift.end_time.date() <= old_end_date
            )
            # Cancel participation for shifts no longer covered by the subscription
            self._cancel_participation_by_shifts(shifts_old_sub_only)
