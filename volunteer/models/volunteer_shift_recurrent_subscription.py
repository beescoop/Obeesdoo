# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class VolunteerShiftRecurrentSubscription(models.Model):
    _name = "volunteer.shift.recurrent.subscription"
    _description = "Shift Recurrent Subscription"
    _order = "start_date"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    # State fields

    active = fields.Boolean(required=True, tracking=True, default=True)
    temporal_state = fields.Selection(
        selection=[
            ("finished", "Finished"),
            ("ongoing", "Ongoing"),
            ("upcoming", "Upcoming"),
        ],
        compute="_compute_temporal_state",
        store=True,
    )

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

    # Compute methods

    @api.depends("start_date", "end_date")
    def _compute_temporal_state(self):
        """Compute temporal_state based on dates."""
        for sub in self:
            sub.temporal_state = sub._get_current_temporal_state()

    # Constraints

    @api.constrains("start_date", "end_date", "generator_id", "active")
    def _check_subscription_dates(self):
        """Check subscriptions dates consistency and within generator period (in this order).
        Skipped for canceled (inactive) subscriptions.
        """
        for sub in self:
            if not sub.active:
                continue
            # Check dates consistency
            if sub.end_date and sub.start_date >= sub.end_date:
                raise ValidationError(
                    _("Start date must be before end date.")
                    + sub._get_conflicting_sub_detail_message()
                )
            gen = sub.generator_id
            gen_start_date = fields.Date.to_date(gen.start_time)
            # Check subscription is within generator period
            if (
                sub.start_date < gen_start_date
                or (gen.until_date and sub.start_date > gen.until_date)
                or (sub.end_date and gen.until_date and sub.end_date > gen.until_date)
            ):
                raise UserError(
                    _("Subscription must be within generator period.")
                    + sub._get_conflicting_sub_detail_message()
                )

    # Override methods

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("active") is False:
                raise UserError(_("Cannot create an inactive subscription."))
            self._check_dates_not_in_past(vals)
        subscriptions = super().create(vals_list)
        for sub in subscriptions:
            if sub.generator_id.state == "confirmed":
                sub.generate_participation()
        return subscriptions

    def write(self, vals):
        self._check_can_be_modified(vals)
        old_sub_data = {}
        for sub in self:
            state = sub._get_current_temporal_state()
            sub._check_dates_not_in_past(vals, temporal_state=state)
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

    def action_cancel_subscription(self):
        """Cancel subscription by setting end_date to today and active to False."""
        self.ensure_one()
        today = fields.Date.today()
        if self._get_current_temporal_state() == "finished":
            raise UserError(_("Cannot cancel a subscription that has already ended."))
        if not self.active:
            raise UserError(_("This subscription is already canceled."))
        self.write(
            {
                "end_date": today,
                "active": False,
            }
        )
        return True

    def _get_current_temporal_state(self):
        """Get current temporal state of the subscription based on dates."""
        self.ensure_one()
        today = fields.Date.today()
        if self.end_date and self.end_date < today:
            return "finished"
        if self.start_date > today:
            return "upcoming"
        return "ongoing"

    def _check_can_be_modified(self, vals):
        """Check if subscription can be modified.

        - Volunteer cannot be changed
        - Canceled (inactive) and finished subscriptions cannot be modified
        - Ongoing subscription start_date cannot be modified
        - Upcoming subscriptions are fully modifiable.
        """
        for sub in self:
            if "volunteer_id" in vals and vals["volunteer_id"] != sub.volunteer_id.id:
                raise UserError(
                    _(
                        "It is not possible to change the volunteer "
                        "of an existing subscription."
                    )
                )
            if not sub.active:
                raise UserError(
                    _("A canceled subscription can't be modified.")
                    + sub._get_conflicting_sub_detail_message()
                )
            current_temporal_state = sub._get_current_temporal_state()
            if current_temporal_state == "finished":
                raise UserError(
                    _("A subscription already finished can't be modified.")
                    + sub._get_conflicting_sub_detail_message()
                )
            if current_temporal_state == "ongoing" and "start_date" in vals:
                raise UserError(
                    _("Start date of an ongoing subscription can't be modified.")
                    + sub._get_conflicting_sub_detail_message()
                )

    def _get_conflicting_sub_detail_message(self):
        """Return a formatted message with details of the subscription
        to append to validation error messages.
        """
        self.ensure_one()
        readable_end_date = self.end_date or "No end date"
        message = (
            f"\n\nConflicting subscription :\n"
            f"Volunteer: {self.volunteer_id.name}\n"
            f"Start date: {self.start_date}\n"
            f"End date: {readable_end_date}\n"
        )
        return message

    def _check_dates_not_in_past(self, vals, temporal_state=None):
        """Check that subscription dates are not in the past.

        For create/upcoming subscriptions: checks start_date only, since end_date
        must be after start_date (validated separately).

        For ongoing subscriptions: checks end_date only, since start_date can
        legitimately be in the past.
        """
        # Allow empty recordset for create(), enforce single record otherwise
        if self:
            self.ensure_one()
        today = fields.Date.today()
        start_date = vals["start_date"] if "start_date" in vals else self.start_date
        # Get end_date from vals if present (can be explicit False to make infinite).
        # If not in vals, use self.end_date which is False when self is empty (create)
        # or when subscription is already infinite (write)
        end_date = vals["end_date"] if "end_date" in vals else self.end_date
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = fields.Date.from_string(start_date)
        if isinstance(end_date, str):
            end_date = fields.Date.from_string(end_date)
        # Create()/upcoming: check start_date only
        if temporal_state is None or temporal_state == "upcoming":
            if start_date < today:
                raise UserError(_("Start date cannot be in the past"))
        # Ongoing: check end_date only
        if temporal_state == "ongoing":
            if end_date and end_date < today:
                raise UserError(_("End date cannot be in the past"))

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
            lambda shift: intersection_start_date
            <= shift.start_time.date()
            <= intersection_end_date
        )
        return shifts_intersection

    def generate_participation(self):
        """Generate participation for all future shifts covered by this subscription.
        Conflicting punctual participation is automatically canceled during generation.
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
                lambda shift: shift.start_time.date() <= self.end_date
            )
        return shifts

    def _generate_participation_by_shifts(self, shifts):
        """Generate participation records for the given shifts
        for the volunteer linked to this subscription.
        This method cancels any conflicting punctual participation before generating
        the recurrent participation.
        """
        self.ensure_one()
        self._cancel_conflicting_punctual_participation(shifts)
        participation_to_create = []
        for shift in shifts:
            participation_to_create.append(
                self._prepare_participation_vals(shift.id, "recurrent", "confirmed")
            )
        return self.env["volunteer.shift.participation"].create(participation_to_create)

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
        """Cancel all confirmed punctual participation on the given shifts
        for this subscription's volunteer.
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
        date_last_shift = future_shifts.sorted("start_time", reverse=True)[
            0
        ].start_time.date()
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
                lambda shift: old_start_date <= shift.start_time.date() <= old_end_date
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
                lambda shift: start_date_full_period
                <= shift.start_time.date()
                <= end_date_full_period
                and shift.id not in shifts_intersection.ids
            )
            # Filter the period of new subscription without intersection and in the full range
            shifts_new_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: new_start_date <= shift.start_time.date() <= new_end_date
            )
            # Generate participation for shifts newly covered by the subscription
            self._generate_participation_by_shifts(shifts_new_sub_only)
            # Filter the period of old subscription without intersection and in the full range
            shifts_old_sub_only = shifts_full_period_without_intersection.filtered(
                lambda shift: old_start_date <= shift.start_time.date() <= old_end_date
            )
            # Cancel participation for shifts no longer covered by the subscription
            self._cancel_participation_by_shifts(shifts_old_sub_only)

    def _prepare_participation_vals(
        self, shift_id, registration_type, registration_state
    ):
        """Prepare vals to create a participation with given registration type and state
        for this subscription's volunteer and the given shift.
        """
        self.ensure_one()
        participation_vals = {
            "shift_id": shift_id,
            "volunteer_id": self.volunteer_id.id,
            "registration_type": registration_type,
            "registration_state": registration_state,
        }
        return participation_vals
