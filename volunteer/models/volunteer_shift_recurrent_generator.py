# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import UserError
from odoo import api, fields, models
from odoo.exceptions import ValidationError
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
            if generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_all_participation()
        return generators

    def write(self, vals):
        old_states = {generator.id: generator.state for generator in self}
        res = super().write(vals)
        for generator in self:
            previous_state = old_states[generator.id]
            # If the generator is confirmed, generate shifts and participation
            if previous_state == "draft" and generator.state == "confirmed":
                generator._generate_shifts()
                generator._generate_all_participation()
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
        shift_generated_start_time = self.start_time
        shift_generated_end_time = self.end_time
        # Skip past occurrences by incrementing with delta until reaching a future date
        while shift_generated_start_time.date() < today:
            shift_generated_start_time += delta
            shift_generated_end_time += delta
        nb_generated_shift = 0
        while (
            nb_generated_shift < nb_occurrence
            and shift_generated_start_time.date() <= generation_end_date
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
            shift_generated_start_time += delta
            shift_generated_end_time += delta
            nb_generated_shift += 1

    def _generate_all_participation(self):
        """Generate participation for all subscriptions in the generator"""
        for subscription in self.volunteer_subscription_ids:
            subscription.generate_participation()
