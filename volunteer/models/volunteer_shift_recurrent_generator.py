# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _


class VolunteerShiftRecurrentGenerator(models.Model):
    _name = "volunteer.shift.recurrent.generator"
    _description = "Recurrent Shift Generator"
    _inherit = ["volunteer.shift.mixin", "mail.thread", "mail.activity.mixin"]

    # State fields

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("canceled", "Canceled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Period fields

    until_date = fields.Date(required=False, tracking=True)
    interval_type = fields.Selection(
        selection=[
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
            ("years", "Years"),
        ],
        required=True,
        tracking=True,
    )
    interval = fields.Integer(
        required=True,
        default=1,
        tracking=True,
    )

    # Relational fields

    volunteer_shift_ids = fields.One2many(
        comodel_name="volunteer.shift",
        inverse_name="generator_id",
        string="Recurrent Shifts",
        tracking=True,
    )
    volunteer_subscription_ids = fields.One2many(
        comodel_name="volunteer.shift.recurrent.subscription",
        inverse_name="generator_id",
        string="Subscriptions",
        tracking=True,
    )

    volunteer_subscription_inactive_ids = fields.One2many(
        comodel_name="volunteer.shift.recurrent.subscription",
        inverse_name="generator_id",
        string="Canceled subscriptions",
        domain=[("active", "=", False)],
        context={"active_test": False},
    )

    # SQL constraints

    _sql_constraints = [
        (
            "gen_max_vol_nb_is_pos",
            "CHECK(max_volunteer_nb > 0)",
            "The maximum of volunteers cannot be null or negative.",
        ),
        (
            "interval_is_pos",
            "CHECK(interval > 0)",
            "The interval cannot be null or negative.",
        ),
    ]

    # Constraints

    @api.constrains("until_date")
    def _check_until_date_not_in_past(self):
        """Check that until_date is not before today."""
        today = fields.Date.today()
        for generator in self:
            if generator.until_date and generator.until_date < today:
                raise UserError(_("The until date cannot be in the past."))

    @api.constrains("start_time", "until_date")
    def _check_start_time_before_until_date(self):
        """Check that start_time is strictly before until_date if not null.
        This constraint is skipped for canceled generator."""
        for generator in self:
            if generator.state != "canceled" and generator.until_date:
                start_date = generator.start_time.date()
                if generator.until_date <= start_date:
                    raise ValidationError(
                        _("The shift start time must be before until date.")
                    )

    # Override methods

    @api.model_create_multi
    def create(self, vals_list):
        generators = super().create(vals_list)
        for generator in generators:
            # Prevent creating generators directly in canceled state
            if generator.state == "canceled":
                raise UserError(_("A generator cannot be created in canceled state."))
            if generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_all_participation()
        return generators

    def write(self, vals):
        old_states = {generator.id: generator.state for generator in self}
        res = super().write(vals)
        for generator in self:
            previous_state = old_states[generator.id]
            if previous_state == "draft" and generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_all_participation()
            elif previous_state != "canceled" and generator.state == "canceled":
                generator._handle_generator_cancellation()
        return res

    # Methods

    def _get_interval_delta(self):
        """Get the interval delta for the generator"""
        self.ensure_one()
        if self.interval_type == "days":
            return timedelta(days=self.interval)
        elif self.interval_type == "weeks":
            return timedelta(weeks=self.interval)
        elif self.interval_type == "months":
            return relativedelta(months=self.interval)
        elif self.interval_type == "years":
            return relativedelta(years=self.interval)
        else:
            raise UserError(_("The interval type is not valid."))

    def _get_ongoing_subscriptions(self):
        """Get all ongoing subscriptions for this generator."""
        self.ensure_one()
        ongoing_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda sub: sub.active and sub._get_current_temporal_state() == "ongoing"
        )
        return ongoing_subscriptions

    def _get_upcoming_subscriptions(self):
        """Get all upcoming subscriptions for this generator."""
        self.ensure_one()
        upcoming_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda sub: sub.active and sub._get_current_temporal_state() == "upcoming"
        )
        return upcoming_subscriptions

    def _get_future_shifts(self):
        """Get all future shifts for this generator."""
        self.ensure_one()
        tomorrow = fields.Date.today() + timedelta(days=1)
        return self.env["volunteer.shift"].search(
            [
                ("generator_id", "=", self.id),
                ("start_time", ">=", tomorrow),
            ]
        )

    def _generate_shifts(self):
        """Generate all shifts from the generator start date
        until the generator until date or number of occurrences,
        using the specified interval.

        When the generator start date is in the past or equal to today,
        shift generation starts strictly from tomorrow (day-based logic).
        No shift is generated for the current day, regardless of the confirmation time.
        """
        self.ensure_one()
        nb_occurrence = self.company_id.shift_nb_occurrence
        stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        delta = self._get_interval_delta()
        today = fields.Date.today()
        # Generate only future shifts
        generation_start_date = (
            today if self.start_time.date() < today else self.start_time.date()
        )
        # Calculate end date from until_date or occurrence count
        if self.until_date:
            generation_end_date = self.until_date
        else:
            generation_end_date = generation_start_date
            for _i in range(nb_occurrence):
                generation_end_date += delta
        shift_to_generate_start_time = self.start_time
        shift_to_generate_end_time = self.end_time
        # Skip past occurrences by incrementing with delta until reaching a future date
        while shift_to_generate_start_time.date() <= today:
            shift_to_generate_start_time += delta
            shift_to_generate_end_time += delta
        nb_shift_to_generate = 0
        shifts_to_create = []
        while (
            nb_shift_to_generate < nb_occurrence
            and shift_to_generate_start_time.date() <= generation_end_date
        ):
            vals = self._prepare_shift_vals(
                shift_to_generate_start_time,
                shift_to_generate_end_time,
                stage_confirmed,
            )
            shifts_to_create.append(vals)
            shift_to_generate_start_time += delta
            shift_to_generate_end_time += delta
            nb_shift_to_generate += 1
        return self.env["volunteer.shift"].create(shifts_to_create)

    def _generate_all_participation(self):
        """Generate participation for all subscriptions in the generator"""
        for subscription in self.volunteer_subscription_ids:
            subscription.generate_participation()

    def _handle_generator_cancellation(self):
        """Handle the cancellation of the generator by:
        - Call action_cancel_subscription() on all active upcoming and ongoing subscriptions
        - Auto-canceling all future shifts
        - Setting the generator until_date to today
        """
        self.ensure_one()
        today = fields.Date.today()
        ongoing_subscriptions = self._get_ongoing_subscriptions()
        upcoming_subscriptions = self._get_upcoming_subscriptions()
        subscriptions_to_canceled = ongoing_subscriptions + upcoming_subscriptions
        for sub in subscriptions_to_canceled:
            sub.action_cancel_subscription()
        # Auto-cancel future shifts, which will also cancel related participation
        future_shifts = self._get_future_shifts()
        future_shifts.write(
            {"stage_id": self.env.ref("volunteer.volunteer_shift_stage_canceled").id}
        )
        # Set until_date to today using super to avoid write recursion
        # (future validations will be added to write method
        # and need to be bypassed)
        res = super(VolunteerShiftRecurrentGenerator, self).write({"until_date": today})
        return res

    def _prepare_shift_vals(self, shift_start_time, shift_end_time, shift_stage):
        """Prepare vals to create a shift in the given stage
        with specified start and end time for this generator.
        """
        self.ensure_one()
        shift_vals = {
            "name": self.name,
            "tz": self.tz,
            "start_time": shift_start_time,
            "end_time": shift_end_time,
            "max_volunteer_nb": self.max_volunteer_nb,
            "stage_id": shift_stage.id,
            "type_id": self.type_id.id,
            "category_id": self.category_id.id,
            "tag_ids": self.tag_ids.ids,
            "generator_id": self.id,
            "company_id": self.company_id.id,
            "coordinator_id": self.coordinator_id.id,
        }
        return shift_vals
