# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from odoo import api, fields, models
from odoo.fields import Date


class VolunteerShiftRecurrentSubscription(models.Model):
    _name = "volunteer.shift.recurrent.subscription"
    _description = "Shift Recurrent Subscription"
    _order = "start_date"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    start_date = fields.Date(required=True, tracking=True, default=Date.today())
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

    # Override methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            requested_start_date = Date.to_date(vals.get("start_date"))
            requested_end_date = Date.to_date(vals.get("end_date"))
            gen_id = vals.get("generator_id")
            if gen_id:
                generator = self.env["volunteer.shift.recurrent.generator"].browse(
                    gen_id
                )
                # Pass vals to proceed with the check on each vals
                # and pass also the full vals_list to verify all the vals requested
                # in multi create for excluding them
                generator.check_remaining_subscription_by_day(vals, vals_list)
                # Cancel eventual participation registered on shifts covered by the new sub
                self._cancel_punctual_participation_for_requested_period(
                    generator.id,
                    vals.get("volunteer_id"),
                    requested_start_date,
                    requested_end_date,
                )
                # Check remaining_slots based on generated shifts can be called before creation
                # because it only adds new participation without needing
                # to update the actual remaining slots for liberating slots
                # like it's the case in write
                generator.check_remaining_slots_by_shift_generated(
                    requested_start_date, requested_end_date
                )
        subscriptions = super().create(vals_list)
        for sub in subscriptions:
            # Generate all participation for new sub requested after all checks pass
            if sub.generator_id.state == "confirmed":
                sub.generate_participation()
        return subscriptions

    def write(self, vals):
        for sub in self:
            generator = sub.generator_id
            # Old values to exclude to avoid counting twice since it's a write operation
            old_sub_vals = {
                "start_date": sub.start_date,
                "end_date": sub.end_date,
                "generator_id": generator.id,
                "volunteer_id": sub.volunteer_id.id,
            }
            # New values with old ones required if unchanged
            requested_vals = {
                "start_date": Date.to_date(vals.get("start_date")) or sub.start_date,
                "end_date": Date.to_date(vals.get("end_date")) or sub.end_date,
                "generator_id": generator.id,
                "volunteer_id": sub.volunteer_id.id,
            }
            generator.check_remaining_subscription_by_day(
                requested_vals, [requested_vals], sub_to_exclude=old_sub_vals
            )
            res = super().write(vals)
            # Cancel eventual punctual participation registered on shifts covered by the new sub
            self._cancel_punctual_participation_for_requested_period(
                generator.id,
                sub.volunteer_id.id,
                requested_vals.get("start_date"),
                requested_vals.get("end_date"),
            )
            # After cancellation of punctual participation,
            # cancel or generate the ones concerned by the new sub
            sub._managing_cancel_or_create_participation(
                old_sub_vals.get("start_date"), old_sub_vals.get("end_date")
            )
            # After the super().write(vals), remaining_slots of concerned shifts
            # are already updated so it's possible to check by generated shifts
            generator.check_remaining_slots_by_shift_generated(
                requested_vals.get("start_date"),
                requested_vals.get("end_date"),
                volunteer_to_exclude=sub.volunteer_id.id,
            )
        return res

    # Methods

    def _get_shifts_intersection_between_two_periods(
        self, new_start_date, new_end_date, old_start_date, old_end_date
    ):
        """Get all shifts in the intersection on two periods"""
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
        new_end_date = self.end_date or self.generator_id.determine_furthest_end_date()
        old_end_date = old_end_date or self.generator_id.determine_furthest_end_date()
        shifts_intersection = self._get_shifts_intersection_between_two_periods(
            self.start_date, new_end_date, old_start_date, old_end_date
        )
        if not shifts_intersection:
            # No intersection : all old shifts need to be canceled
            old_shifts = self.generator_id.volunteer_shift_ids.filtered(
                lambda shift: shift.start_time.date() >= old_start_date
                and shift.end_time.date() <= old_end_date
            )
            self._cancel_participation_by_shifts(old_shifts)
            # All shifts covered by the new subscription need to be generated
            # Apply generate_participation without args because new vals are already in self
            # (management method called after super().write())
            self.generate_participation()
        else:
            # Define the boundaries of the full period between old and new subscription
            start_date_full_period = min(self.start_date, old_start_date)
            end_date_full_period = max(new_end_date, old_end_date)
            # Filter the full period excluding the intersection period
            shifts_full_period_without_intersection = (
                self.generator_id.volunteer_shift_ids.filtered(
                    lambda shift: shift.start_time.date() >= start_date_full_period
                    and shift.end_time.date() <= end_date_full_period
                    and shift.id not in shifts_intersection.ids
                )
            )
            # Filter the period of new subscription without intersection and in the full range
            shifts_new_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: shift.start_time.date() >= self.start_date
                and shift.end_time.date() <= new_end_date
            )
            # The shifts after modification which are only concerned
            # by the new subscription need to be generated
            self._generate_participation_by_shifts(shifts_new_sub_only)
            # Filter the period of old subscription without intersection and in the full range
            shifts_old_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: shift.start_time.date() >= old_start_date
                and shift.end_time.date() <= old_end_date
            )
            # The shifts after modification which are only concerned
            # by the old subscription need to be canceled
            self._cancel_participation_by_shifts(shifts_old_sub_only)

    @api.model
    def _cancel_punctual_participation_for_requested_period(
        self, generator_id, volunteer_id, requested_start_date, requested_end_date
    ):
        """Cancel the punctual participation of a volunteer if they subscribe
        for a period when they already have punctual participation registered.

        This is a static method because it's called in create()
        and self doesn't contain the useful vals,
        so it's necessary to pass them explicitly.
        It cannot be used after super().create()
        because the cancellation needs to be done beforehand
        to avoid counting twice the participation of the same
        volunteer during checks applied on remaining_slots by shift.
        """
        # Generator needs to be retrieved from the generator_id provided
        generator = self.env["volunteer.shift.recurrent.generator"].browse(generator_id)
        for shift in generator.volunteer_shift_ids:
            if not requested_end_date:
                end_date_to_check = generator.determine_furthest_end_date()
            else:
                end_date_to_check = requested_end_date
            if requested_start_date <= shift.start_time.date() <= end_date_to_check:
                # Search for punctual participation for this volunteer
                # during the requested period
                participation_to_cancel = self.env[
                    "volunteer.shift.participation"
                ].search(
                    [
                        ("shift_id", "=", shift.id),
                        ("volunteer_id", "=", volunteer_id),
                        ("registration_type", "!=", "recurrent"),
                    ]
                )
                # If the volunteer has punctual participation, it has to be canceled
                if participation_to_cancel:
                    participation_to_cancel.write(
                        {
                            "registration_state": "canceled",
                        }
                    )

    def _cancel_participation_by_shifts(self, shifts):
        """Cancel all participation for given shifts
        for the volunteer concerned by subscription in self"""
        self.ensure_one()
        for shift in shifts:
            participation_to_cancel = self.env["volunteer.shift.participation"].search(
                [
                    ("shift_id", "=", shift.id),
                    ("volunteer_id", "=", self.volunteer_id.id),
                ]
            )
            if participation_to_cancel:
                participation_to_cancel.write(
                    {
                        "registration_state": "canceled",
                    }
                )

    def _generate_participation_by_shifts(self, shifts):
        """Generate all participation for given shifts
        for the volunteer concerned by subscription in self"""
        self.ensure_one()
        for shift in shifts:
            self.env["volunteer.shift.participation"].create(
                {
                    "shift_id": shift.id,
                    "volunteer_id": self.volunteer_id.id,
                    "registration_type": "recurrent",
                    "registration_state": "confirmed",
                }
            )

    def generate_participation(self):
        """Generate participation for all shifts covered by the subscription in self"""
        self.ensure_one()
        generator = self.generator_id
        end_date = self.end_date
        if not end_date:
            end_date = generator.determine_furthest_end_date()
        for shift in generator.volunteer_shift_ids:
            if (
                self.start_date <= shift.start_time.date()
                and end_date >= shift.end_time.date()
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
