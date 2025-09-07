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

    nb_occurrence = fields.Integer(default=10)
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
    @api.constrains("until_date")
    def _check_sub_date_range_in_generator_future_period(self):
        for sub in self.volunteer_subscription_ids:
            try:
                sub.check_date_range_in_generator_period(self)
            except ValidationError as e:
                # If check doesn't pass, return a more specialized error message
                # concerning until_date modification
                raise ValidationError(
                    _(
                        f"Cannot modify the generator's end date: this change would exclude "
                        f"at least one existing subscription from the valid period."
                        f"{sub.get_conflicting_sub_detail_message()}"
                    )
                ) from e

    @api.constrains("max_volunteer_nb", "volunteer_subscription_ids")
    def _check_max_volunteer_nb_lower_than_nb_subscriptions(self):
        """Check that the number of subscriptions for period
        does not exceed the maximum number of subscriptions allowed for the generator."""
        for generator in self:
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
                except ValidationError as e:
                    # If check doesn't pass, return a more specialized error message
                    # concerning the max modification
                    raise ValidationError(
                        _(
                            f"The maximum number of volunteers ({generator.max_volunteer_nb}) "
                            f"cannot be lower than the number "
                            f"of subscribed volunteers during the same period."
                        )
                    ) from e

    # Override methods
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Ensure that until_date is not before start_time
            if vals.get("until_date"):
                until_date = fields.Date.to_date(vals["until_date"])
                start_time = fields.Datetime.to_datetime(vals["start_time"])
                if until_date < start_time.date():
                    raise ValidationError(
                        _(
                            "The generator end date cannot be earlier "
                            "than the period start date."
                        )
                    )

        return super().create(vals_list)

    def write(self, vals):
        # Restrict state change to admins only
        if (
            "state" in vals
            and not self.env.context.get("install_mode")
            and not self.env.user.has_group("volunteer.volunteer_group_admin")
        ):
            raise AccessError(_("Only admins can change the state of a generator"))
        for generator in self:
            # Prevent modification of fields when the generator is not in draft state
            # except when canceling the generator without other changes
            if (
                generator.state != "draft"
                and not (vals.get("state") == "canceled" and len(vals) == 1)
                and not vals.get("volunteer_subscription_ids")
            ):
                raise ValidationError(
                    _("Only generators in draft can be modified.")
                    + self._get_message_procedure_to_modify_generator_fields()
                )
            new_until_date = (
                fields.Date.to_date(vals.get("until_date")) or generator.until_date
            )
            new_start_time = (
                fields.Datetime.to_datetime(vals.get("start_time"))
                or generator.start_time
            )
            # Ensure that until_date is not before start_time
            if new_until_date and new_until_date < new_start_time.date():
                raise ValidationError(
                    _("The generator end date cannot be earlier than the start date.")
                )
        old_states = {generator.id: generator.state for generator in self}
        res = super().write(vals)
        for generator in self:
            today = date.today()
            previous_state = old_states[generator.id]
            # Unauthorize return to state draft
            if previous_state != "draft" and generator.state == "draft":
                raise ValidationError(_("Returning to draft state is not allowed."))
            # Unauthorize return from canceled state
            if previous_state == "canceled" and generator.state != "canceled":
                raise ValidationError(
                    _("It is not possible to change the state of a canceled generator.")
                )
            # If the generator is confirmed, generate shifts and participation
            if previous_state == "draft" and generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_participation()
            # Else, if the generator is canceled, apply the required changes
            elif previous_state != "canceled" and generator.state == "canceled":
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
                # Set until_date to today after other operations
                # using super to avoid recursion and bypass checks
                super(VolunteerShiftRecurrentGenerator, generator).write(
                    {"until_date": today}
                )
        return res

    # Methods

    def determine_furthest_end_date(self):
        """Determine the furthest end date to use when
        end_date or until_date are not provided."""
        self.ensure_one()
        if self.until_date:
            return self.until_date
        furthest_end_date = self.start_time.date()
        # Find the furthest end_date among existing subscriptions
        if self.volunteer_subscription_ids:
            sub_with_ends = self.volunteer_subscription_ids.filtered(
                lambda sub: sub.end_date
            )
            furthest_start_date = max(
                self.volunteer_subscription_ids.mapped("start_date")
            )
            # If no subscription has an end_date, and there is no until_date,
            # furthest_end_date will be the furthest start_date
            if sub_with_ends:
                furthest_end_date = max(sub_with_ends.mapped("end_date"))
            if furthest_end_date < furthest_start_date:
                furthest_end_date = furthest_start_date
        # Find the furthest end_date among existing participation
        if self.volunteer_shift_ids:
            all_confirmed_participation = self.env[
                "volunteer.shift.participation"
            ].search(
                [
                    ("shift_id", "in", self.volunteer_shift_ids.ids),
                    ("registration_type", "!=", "recurrent"),
                    ("registration_state", "=", "confirmed"),
                ]
            )
            for participation in all_confirmed_participation:
                end_date = participation.shift_id.start_time.date()
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
                        if requested_end_date != self.determine_furthest_end_date():
                            custom_date_message = (
                                f"for the period {requested_start_date} "
                                f"to {requested_end_date}.\n"
                            )
                        else:
                            custom_date_message = (
                                f"from {requested_start_date} "
                                f"until the end of the generator.\n"
                            )
                        raise ValidationError(
                            _(
                                f"It is not possible to subscribe"
                                f" volunteers in this generator, "
                                f"{custom_date_message}"
                                f"Some shifts in this period are already at maximum capacity"
                                f" ({self.max_volunteer_nb}) due to individual participation."
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
            fields.Date.to_date(requested_sub.get("end_date"))
            or self.determine_furthest_end_date()
        )
        date_to_check = fields.Date.to_date(requested_sub.get("start_date"))
        while date_to_check <= requested_end_date:
            # Check that a volunteer can only be registered once in the same period
            self._check_unique_volunteer_subscription(
                date_to_check, requested_end_date, requested_sub_list, sub_to_exclude
            )
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
                if requested_sub.get("end_date"):
                    custom_date_message = (
                        f"for the period {requested_start_date}"
                        f" to {requested_end_date}.\n"
                    )
                else:
                    custom_date_message = (
                        f"from {requested_start_date} until the end of the generator.\n"
                    )

                raise ValidationError(
                    _(
                        f"It is not possible to subscribe"
                        f" volunteers in this generator, "
                        f"{custom_date_message}"
                        f" The maximum capacity is "
                        f"{self.max_volunteer_nb}."
                    )
                )
            date_to_check = date_to_check + timedelta(days=1)
        return True

    def _check_unique_volunteer_subscription(
        self, date_to_check, requested_end_date, requested_sub_list, sub_to_exclude=None
    ):
        """Check that a volunteer can only be registered once in the same period"""
        self.ensure_one()
        # Get active subscriptions for the day to check by
        # giving the same date as start and end date
        active_subscriptions = self._get_active_subscriptions_for_period(
            requested_start_date=date_to_check,
            requested_end_date=date_to_check,
        )
        existing_volunteer_ids = active_subscriptions.volunteer_id.ids
        # Exclude the volunteer of sub_to_exclude (if given)
        # from existing_volunteer_ids
        # and if the subscription covers the date_to_check
        # to avoid double counting during write operation
        if (
            sub_to_exclude
            and sub_to_exclude.get("generator_id") == self.id
            and sub_to_exclude.get("start_date")
            <= date_to_check
            <= (sub_to_exclude.get("end_date") or self.determine_furthest_end_date())
        ):
            volunteer_to_exclude = sub_to_exclude.get("volunteer_id")
            filtered_list = []
            # Filter existing_volunteer_ids to exclude volunteer_to_exclude
            for volunteer_id in existing_volunteer_ids:
                if volunteer_id != volunteer_to_exclude:
                    filtered_list.append(volunteer_id)
            existing_volunteer_ids = filtered_list
        # If a new subscription is requested with no end_date
        # we have to consider the furthest end date
        # among all new subscriptions in requested_sub_list
        # to prevent using a too short end date
        # since determine_furthest_end_date()
        # cannot consider new requested subscriptions
        new_sub_list_furthest_end = requested_end_date
        for sub_in_list in requested_sub_list:
            if sub_in_list.get("generator_id") == self.id and sub_in_list.get(
                "end_date"
            ):
                sub_end = fields.Date.to_date(sub_in_list.get("end_date"))
                if sub_end > new_sub_list_furthest_end:
                    new_sub_list_furthest_end = sub_end
        # Get new volunteer_ids from requested_sub_list
        # considering only subscriptions active on date_to_check
        # and using the furthest end date of the list
        # if no end_date is provided for a subscription
        new_volunteer_ids = []
        for new_sub in requested_sub_list:
            if new_sub.get("generator_id") == self.id:
                new_start = fields.Date.to_date(new_sub.get("start_date"))
                new_end = (
                    fields.Date.to_date(new_sub.get("end_date"))
                    or new_sub_list_furthest_end
                )
                if new_start <= date_to_check <= new_end:
                    new_volunteer_ids.append(new_sub.get("volunteer_id"))
        # Combine existing and new volunteer ids
        all_volunteer_ids = existing_volunteer_ids + new_volunteer_ids
        # Check uniqueness
        if len(all_volunteer_ids) != len(set(all_volunteer_ids)):
            raise ValidationError(
                _("A volunteer can only be registered once in the same period.")
            )
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
            new_sub_start_date = fields.Date.to_date(new_sub.get("start_date"))
            new_sub_end_date = fields.Date.to_date(new_sub.get("end_date"))
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
        furthest_end_date = self.determine_furthest_end_date()
        if not requested_end_date:
            requested_end_date = furthest_end_date
        # Filter existing subscriptions by intersection between each subscription's period
        # and the requested period to check
        active_subscriptions = self.volunteer_subscription_ids.filtered(
            lambda subscription: subscription.start_date <= requested_end_date
            and requested_start_date <= (subscription.end_date or furthest_end_date)
        )
        return active_subscriptions

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

    def _get_message_procedure_to_modify_generator_fields(self):
        """Get the message explaining the procedure to modify restricted fields
        or indicate to contact the administrator"""
        if not self.env.user.has_group("volunteer.volunteer_group_admin"):
            custom_message = (
                "\nContact your administrator to make this change by "
                "applying the requested procedure."
            )
        else:
            custom_message = (
                "\nTo modify generator:\n"
                "- Duplicate the generator and set the start time to today (or later)\n"
                "- Apply the changes and re-add old subscriptions if needed\n"
                "- Confirm the new generator, then cancel the original one.\n"
            )
        return custom_message

    def _generate_shifts(self):
        """Generate all shifts from the generator start date
        until the generator end date, using the specified interval."""
        self.ensure_one()
        stage_confirmed = self.env.ref("volunteer.volunteer_shift_stage_confirmed")
        delta = self._get_interval_delta()
        today = date.today()
        # Generate only future shifts
        generation_start_date = (
            today if self.start_time.date() < today else self.start_time.date()
        )
        # Determine generation end date
        if self.until_date:
            generation_end_date = self.until_date
        else:
            # If no until_date is provided, determine the end date
            # based on the number of occurrences
            generation_end_date = generation_start_date
            for _i in range(self.nb_occurrence):
                generation_end_date += delta
        # Determine the start_time and end_time for the first generated shift
        if self.start_time.date() < today:
            day_diff = (today - self.start_time.date()).days
            shift_generated_start_time = self.start_time + timedelta(days=day_diff)
            shift_generated_end_time = self.end_time + timedelta(days=day_diff)
        else:
            shift_generated_start_time = self.start_time
            shift_generated_end_time = self.end_time
        # Generate shifts until reaching the end date or the number of occurrences
        while (
            len(self.volunteer_shift_ids) < self.nb_occurrence
            and generation_start_date <= generation_end_date
        ):
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
