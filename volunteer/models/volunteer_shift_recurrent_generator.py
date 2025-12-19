# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
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

    # SQL constraints

    _sql_constraints = [
        (
            "gen_max_vol_nb_is_pos",
            "check (max_volunteer_nb > 0)",
            "The maximum of volunteers cannot be null or negative.",
        ),
        (
            "interval_is_pos",
            "check (interval > 0)",
            "The interval cannot be null or negative.",
        ),
    ]

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

    def _get_active_subscriptions(self):
        """Get all active subscriptions for this generator."""
        self.ensure_one()
        today = fields.Date.today()
        active_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda subscription: subscription.start_date <= today
            and (not subscription.end_date or subscription.end_date >= today)
        )
        return active_subscriptions

    def _get_future_subscriptions(self):
        """Get all future subscriptions for this generator."""
        self.ensure_one()
        today = fields.Date.today()
        future_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda subscription: subscription.start_date >= today
        )
        return future_subscriptions

    def _get_future_shifts(self):
        """Get all future shifts for this generator."""
        self.ensure_one()
        today = fields.Date.today()
        return self.volunteer_shift_ids.filtered(
            lambda shift: shift.start_time.date() >= today
        )

    def _generate_shifts(self):
        """Generate all shifts from the generator start date
        until the generator until date or number of occurrences,
        using the specified interval.
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
        while shift_to_generate_start_time.date() < today:
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
        - Setting the end_date of all future subscriptions to today
        - Auto-canceling all future shifts
        - Setting the generator until_date to today
        """
        self.ensure_one()
        today = fields.Date.today()
        active_subscriptions = self._get_active_subscriptions()
        future_subscriptions = self._get_future_subscriptions()
        subscriptions_to_canceled = active_subscriptions + future_subscriptions
        subscriptions_to_canceled.write({"end_date": today})
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
