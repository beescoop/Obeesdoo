# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.translate import _


class VolunteerShiftRecurrentGenerator(models.Model):
    _name = "volunteer.shift.recurrent.generator"
    _description = "Recurrent Shift Generator"
    _inherit = ["volunteer.shift.mixin", "mail.thread", "mail.activity.mixin"]

    # General fields

    name = fields.Char(required=True, tracking=True)

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

    until_date = fields.Date(required=True, tracking=True)
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
            "interval_is_positive",
            "check (interval > 0)",
            "The interval cannot be null or negative.",
        ),
    ]

    # Constraints

    @api.constrains("max_volunteer_nb", "volunteer_subscription_ids")
    def _check_can_accept_new_subscription(self):
        """Check that the number of confirmed subscriptions for the same period
        does not exceed the maximum number of subscriptions allowed for the generator."""
        for generator in self:
            for subscription in generator.volunteer_subscription_ids:
                requested_start_date = subscription.start_date
                requested_end_date = subscription.end_date
                booking_status = generator.get_booking_status(
                    requested_start_date, requested_end_date
                )
                if not booking_status["can_accept_subscription"]:
                    nb_active_subscriptions = booking_status["nb_active_subscriptions"]
                    raise ValidationError(
                        _(
                            f"The number of subscribed volunteers ({nb_active_subscriptions}) "
                            f"for the period from {requested_start_date} "
                            f"to {requested_end_date} "
                            f"exceeds the generator's maximum allowed "
                            f"({generator.max_volunteer_nb})."
                        )
                    )

    @api.constrains("volunteer_subscription_ids")
    def _check_unique_volunteer_subscription(self):
        """Check that a volunteer can only be registered once
        for the same period at the same generator"""
        for generator in self:
            for subscription in generator.volunteer_subscription_ids:
                requested_start_date = subscription.start_date
                requested_end_date = subscription.end_date
                active_subscriptions = generator.get_booking_status(
                    requested_start_date, requested_end_date
                )["active_subscriptions"]
                active_volunteer_ids = [
                    subscription.volunteer_id.id
                    for subscription in active_subscriptions
                ]
                if len(active_volunteer_ids) != len(set(active_volunteer_ids)):
                    raise ValidationError(
                        _(
                            f"A volunteer can only be registered once for the same period."
                            f"\n{subscription.volunteer_id.name} is already registered "
                            f"from {requested_start_date} to {requested_end_date}."
                        )
                    )

    # Override methods

    def write(self, vals):
        # Restrict state change to admins only
        if (
            "state" in vals
            and not self.env.context.get("install_mode")
            and not self.env.user.has_group("volunteer.volunteer_group_admin")
        ):
            raise AccessError(_("Only admins can change the state of a generator"))
        old_states = {generator.id: generator.state for generator in self}
        res = super().write(vals)
        for generator in self:
            today = date.today()
            previous_state = old_states[generator.id]
            # If the generator is confirmed, generate shifts and participation
            if previous_state == "draft" and generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_participation()
            # Else, if the generator is canceled, apply the required changes
            elif previous_state != "canceled" and generator.state == "canceled":
                super(VolunteerShiftRecurrentGenerator, generator).write(
                    {"until_date": today}
                )
                # Change end_date future subscription
                future_subscriptions = generator.get_booking_status(
                    requested_start_date=today, requested_end_date=generator.until_date
                )["active_subscriptions"]
                for subscription in generator.volunteer_subscription_ids:
                    if subscription in future_subscriptions:
                        subscription.write({"end_date": today})
                # Auto-cancel future shifts, which will also cancel related participation
                future_shifts = generator.volunteer_shift_ids.filtered(
                    lambda shift: shift.start_time.date() >= today
                )
                for shift in future_shifts:
                    shift.write(
                        {
                            "stage_id": self.env.ref(
                                "volunteer.volunteer_shift_stage_canceled"
                            ).id
                        }
                    )
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
            raise ValidationError(_("The interval type is not valid."))

    def _generate_shifts(self):
        """Generate all shifts from the generator start date (or today, if start is in the past)
        until the generator end date, using the specified interval."""
        self.ensure_one()
        stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        today = date.today()
        delta = self._get_interval_delta()
        generation_end_date = self.until_date
        generation_start_date = (
            today if self.start_time.date() < today else self.start_time.date()
        )
        shift_generated_start_time = self.start_time
        shift_generated_end_time = self.end_time
        while generation_start_date <= generation_end_date:
            self.env["volunteer.shift"].create(
                {
                    "name": self.name,
                    "tz": self.tz,
                    "start_time": shift_generated_start_time,
                    "end_time": shift_generated_end_time,
                    "max_volunteer_nb": self.max_volunteer_nb,
                    "stage_id": stage_confirmed.id,
                    "type_id": self.type_id.id,
                    "category_id": self.category_id.id,
                    "tag_ids": self.tag_ids.ids,
                    "generator_id": self.id,
                    "company_id": self.company_id.id,
                    "coordinator_id": self.coordinator_id.id,
                }
            )
            generation_start_date += delta
            shift_generated_start_time += delta
            shift_generated_end_time += delta

    def _generate_participation(self):
        """Generate participation for all subscriptions in the generator"""
        for subscription in self.volunteer_subscription_ids:
            subscription.generate_participation()

    def get_active_subscriptions(self, requested_start_date, requested_end_date):
        """Get the generator active subscriptions for the given period"""
        self.ensure_one()
        active_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda subscription: subscription.start_date <= requested_start_date
            and (
                subscription.end_date >= requested_end_date
                or (
                    subscription.start_date <= requested_end_date
                    and requested_start_date <= subscription.end_date
                )
            )
        )
        return active_subscriptions

    def get_booking_status(self, requested_start_date, requested_end_date):
        """Get the generator booking status for the given period
         by returning a dictionary of :
        - can_accept_subscription: boolean indicating if the generator
        can accept new subscription for the given period
        - active_subscriptions: recordset of active subscription for the given period
        - nb_active_subscriptions: number of active subscription for the given period
        """
        self.ensure_one()
        active_subscriptions = self.get_active_subscriptions(
            requested_start_date, requested_end_date
        )
        nb_active_subscriptions = len(active_subscriptions)
        booking_status = {
            "can_accept_subscription": True,
            "active_subscriptions": active_subscriptions,
            "nb_active_subscriptions": nb_active_subscriptions,
        }
        if self.max_volunteer_nb < nb_active_subscriptions:
            booking_status["can_accept_subscription"] = False
        return booking_status
