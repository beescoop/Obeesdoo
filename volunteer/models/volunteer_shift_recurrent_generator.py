# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.fields import Date
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
            "interval_is_positive",
            "check (interval > 0)",
            "The interval cannot be null or negative.",
        ),
    ]

    # Constraints
    @api.constrains("max_volunteer_nb", "volunteer_subscription_ids")
    def _check_max_volunteer_nb_lower_than_nb_subscriptions(self):
        """Check that the number of subscriptions for period
        does not exceed the maximum number of subscriptions allowed for the generator."""
        for generator in self:
            # Max volunteer number can only be modified when generator is in draft status,
            # no verification on generated shifts and no guarantee for eventual modifications
            # on confirmed generators
            # Note : This limitation is not yet implemented - currently allows modification
            # in any state
            if generator.state == "draft":
                # Build a simulated full period that covers the complete generator period
                # to pass to the check method and launch the global verification
                end_date = generator.determine_furthest_end_date()
                full_period_vals = {
                    "start_date": generator.start_time.date(),
                    "end_date": end_date,
                    "generator_id": generator.id,
                }
                try:
                    # The full period has to be excluded to avoid counting it as a subscription
                    generator.check_remaining_subscription_by_day(
                        full_period_vals,
                        [full_period_vals],
                        sub_to_exclude=full_period_vals,
                    )
                except ValidationError:
                    # If check doesn't pass, return a more specialized error message
                    # concerning the max modification
                    raise ValidationError(
                        f"The maximum number of volunteers ({generator.max_volunteer_nb}) "
                        f"cannot be lower than the number "
                        f"of subscribed volunteers during the same period."
                    ) from None

    @api.constrains("volunteer_subscription_ids")
    def _check_unique_volunteer_subscription(self):
        """Check that a volunteer can only be subscribed once
        for the same period at the same generator"""
        for generator in self:
            for subscription in generator.volunteer_subscription_ids:
                requested_start_date = subscription.start_date
                requested_end_date = subscription.end_date
                # Get the subscriptions with at least one day in the requested period
                active_subscriptions = generator._get_active_subscriptions_for_period(
                    requested_start_date, requested_end_date
                )
                # List ids of volunteers with subscription in the active_subscriptions
                active_volunteer_ids = [
                    subscription.volunteer_id.id
                    for subscription in active_subscriptions
                ]
                # If length of active_volunteer_ids is different
                # from the len of its set (which removes duplicates)
                # it means there are a duplicate so the volunteer appears twice
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
                # Change end_date of future subscriptions by getting the active_subscription
                # for the period from today to generator until_date aka future_subscriptions
                future_subscriptions = generator._get_active_subscriptions_for_period(
                    requested_start_date=today, requested_end_date=generator.until_date
                )
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

    def determine_furthest_end_date(self):
        """Determine the furthest end date to use when
        end_date or until_date are not provided."""
        self.ensure_one()
        furthest_end_date = self.start_time.date()
        if self.volunteer_subscription_ids:
            # Find the furthest end_date among existing subscriptions
            for sub in self.volunteer_subscription_ids:
                if sub.end_date and sub.end_date > furthest_end_date:
                    furthest_end_date = sub.end_date
        # Find the furthest end_date among existing participation
        if self.volunteer_shift_ids:
            # Search all participation on generated shifts
            all_confirmed_participation = self.env[
                "volunteer.shift.participation"
            ].search(
                [
                    ("shift_id", "in", self.volunteer_shift_ids.ids),
                    ("registration_state", "=", "confirmed"),
                ]
            )
            for participation in all_confirmed_participation:
                end_date = participation.shift_end_time.date()
                # Check if any participation extend beyond current furthest date
                if end_date > furthest_end_date:
                    furthest_end_date = end_date
        # Add one day to ensure all null end_dates are grouped together
        # and extend beyond any specific end_date
        furthest_end_date = furthest_end_date + timedelta(days=1)
        return furthest_end_date

    def check_remaining_slots_by_shift_generated(
        self, requested_start_date, requested_end_date=None, volunteer_to_exclude=None
    ):
        """Ensure there are available slots on shifts
        for the specified subscription period.
        volunteer_to_exclude is used during write to exclude
        the volunteer's existing participation from the remaining slots calculation
        to avoid double counting"""
        self.ensure_one()
        if not requested_end_date:
            requested_end_date = self.determine_furthest_end_date()
        date_to_check = requested_start_date
        while date_to_check <= requested_end_date:
            for shift in self.volunteer_shift_ids:
                if shift.start_time.date() <= date_to_check <= shift.end_time.date():
                    remaining_slots = shift.remaining_slots
                    if volunteer_to_exclude:
                        # If volunteer to exclude already has a participation
                        # registered for this shift, it has to be considered
                        # as a free slot to avoid double counting
                        existing_participation = self.env[
                            "volunteer.shift.participation"
                        ].search(
                            [
                                ("shift_id", "=", shift.id),
                                ("volunteer_id", "=", volunteer_to_exclude),
                                ("registration_state", "=", "confirmed"),
                            ]
                        )
                        if existing_participation:
                            remaining_slots += 1
                    if remaining_slots <= 0:
                        raise ValidationError(
                            _(
                                f"It is not possible to subscribe"
                                f" volunteers in this generator, "
                                f"for the period {requested_start_date}"
                                f"to {requested_end_date}."
                                f" The maximum capacity is "
                                f"{self.max_volunteer_nb}."
                            )
                        )
            date_to_check = date_to_check + timedelta(days=1)
        return True

    def check_remaining_subscription_by_day(
        self, requested_sub, requested_sub_list, sub_to_exclude=None
    ):
        """Ensure there are available subscription slots for the specified period.
        sub_to_exclude is used during write and contains the subscription data
        of the current sub being modified so it has to be excluded from the counting
        to avoid counting twice"""
        self.ensure_one()
        requested_end_date = (
            Date.to_date(requested_sub.get("end_date"))
            or self.determine_furthest_end_date()
        )
        # start_date comes from vals during create so it's a string
        # and has to be converted
        date_to_check = Date.to_date(requested_sub.get("start_date"))
        while date_to_check <= requested_end_date:
            count = self._count_nb_new_sub_given_day(
                target_date=date_to_check,
                requested_sub_list=requested_sub_list,
                excluded_sub=sub_to_exclude,
            )
            count += self._count_nb_existing_sub_given_day(
                target_date=date_to_check, excluded_sub=sub_to_exclude
            )
            if count > self.max_volunteer_nb:
                requested_start_date = requested_sub.get("start_date")
                raise ValidationError(
                    _(
                        f"It is not possible to subscribe"
                        f" volunteers in this generator, "
                        f"for the period {requested_start_date} to "
                        f"{requested_end_date}."
                        f" The maximum capacity is "
                        f"{self.max_volunteer_nb}."
                    )
                )
            date_to_check = date_to_check + timedelta(days=1)
        return True

    def _count_nb_new_sub_given_day(
        self, target_date, requested_sub_list, excluded_sub
    ):
        """Count the total number of subscriptions for the requested date
        in vals_list"""
        self.ensure_one()
        filtered_sub_list = []
        # Filter requested_sub_list to process only the current generator's subscriptions
        for requested_sub in requested_sub_list:
            if requested_sub.get("generator_id") == self.id:
                filtered_sub_list.append(requested_sub)
        count = 0
        for new_sub in filtered_sub_list:
            # new_sub_start_date in requested_sub_list comes from vals_list
            # during create so it's a string and has to be converted
            new_sub_start_date = Date.to_date(new_sub.get("start_date"))
            new_sub_end_date = Date.to_date(new_sub.get("end_date"))
            if not new_sub_end_date:
                new_sub_end_date = self.determine_furthest_end_date()
            # If excluded_sub is provided, skip the check for those values
            # to avoid counting them, useful during write operation
            if excluded_sub is not None:
                exclude_sub_end_date = (
                    excluded_sub.get("end_date") or self.determine_furthest_end_date()
                )
                if (
                    excluded_sub.get("start_date") == new_sub_start_date
                    and exclude_sub_end_date == new_sub_end_date
                    and excluded_sub.get("volunteer_id") == new_sub.get("volunteer_id")
                ):
                    continue
            if new_sub_start_date <= target_date <= new_sub_end_date:
                count += 1
        return count

    def _count_nb_existing_sub_given_day(self, target_date, excluded_sub):
        """Count the total number of subscriptions for the requested date
        in existing subscriptions"""
        self.ensure_one()
        count = 0
        for existing_sub in self.volunteer_subscription_ids:
            existing_sub_end_date = (
                existing_sub.end_date or self.determine_furthest_end_date()
            )
            # If excluded_sub is provided, skip the check for those values
            # to avoid counting them, useful during write operation
            if excluded_sub is not None:
                excluded_sub_end_date = (
                    excluded_sub.get("end_date") or self.determine_furthest_end_date()
                )
                if (
                    existing_sub.start_date == excluded_sub.get("start_date")
                    and existing_sub_end_date == excluded_sub_end_date
                    and existing_sub.volunteer_id.id == excluded_sub.get("volunteer_id")
                ):
                    continue
            if existing_sub.start_date <= target_date <= existing_sub_end_date:
                count += 1
        return count

    def _get_active_subscriptions_for_period(
        self, requested_start_date, requested_end_date
    ):
        """Get the generator active subscriptions for the given period"""
        self.ensure_one()
        if not requested_end_date:
            requested_end_date = self.determine_furthest_end_date()
        # Filter existing subscriptions by intersection between each subscription's period
        # and the requested period to check
        active_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda subscription: subscription.start_date <= requested_end_date
            and requested_start_date
            <= (subscription.end_date or self.determine_furthest_end_date())
        )
        return active_subscriptions

    def _generate_shifts(self):
        """Generate all shifts from the generator start date
        until the generator end date, using the specified interval."""
        self.ensure_one()
        stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        delta = self._get_interval_delta()
        generation_end_date = self.until_date or self.determine_furthest_end_date()
        generation_start_date = self.start_time.date()
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
