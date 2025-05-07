# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models
from odoo.tools import format_datetime

from odoo.addons.base.models.res_partner import _tz_get


class VolunteerShiftMixin(models.AbstractModel):
    _name = "volunteer.shift.mixin"
    _description = "Mixin class for shift setup"
    _abstract = True

    # General fields

    name = fields.Char(required=True, tracking=True)
    max_volunteer_nb = fields.Integer(
        string="Max Volunteer", required=True, tracking=True
    )
    is_one_day = fields.Boolean(compute="_compute_is_one_day")

    # Date fields

    tz = fields.Selection(
        selection=_tz_get,
        string="Timezone",
        default=lambda self: self.env.user.tz or "UTC",
        required=True,
        tracking=True,
        help="Timezone of the shift.",
    )
    start_time = fields.Datetime(
        default=fields.Datetime.now(), required=True, tracking=True
    )
    end_time = fields.Datetime(
        default=fields.Datetime.now(), required=True, tracking=True
    )
    start_time_located = fields.Char(compute="_compute_start_time_located")
    end_time_located = fields.Char(compute="_compute_end_time_located")

    # Classification fields

    type_id = fields.Many2one(
        comodel_name="volunteer.shift.type", string="Type", required=True, tracking=True
    )
    category_id = fields.Many2one(
        comodel_name="volunteer.shift.category", string="Category", tracking=True
    )
    tag_ids = fields.Many2many(
        comodel_name="volunteer.shift.tag", string="Tags", tracking=True
    )

    # Relational fields

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
        tracking=True,
    )
    coordinator_id = fields.Many2one(
        comodel_name="res.partner",
        domain="[('is_company', '=', False)]",
        string="Coordinator",
        tracking=True,
    )

    # SQL constraints

    _sql_constraints = [
        (
            "max_volunteer_nb_is_positive",
            "check (max_volunteer_nb > 0)",
            "The maximum of volunteers per shift cannot be null or negative.",
        ),
    ]

    # Compute methods

    @api.depends("start_time", "end_time", "tz")
    def _compute_is_one_day(self):
        for shift in self:
            shift = shift._set_tz_context()
            if shift.start_time and shift.end_time:
                start_date = fields.Datetime.context_timestamp(
                    shift, shift.start_time
                ).date()
                end_date = fields.Datetime.context_timestamp(
                    shift, shift.end_time
                ).date()
                shift.is_one_day = start_date == end_date
            else:
                shift.is_one_day = False

    @api.depends("tz", "start_time")
    def _compute_start_time_located(self):
        for shift in self:
            if shift.start_time:
                shift.start_time_located = format_datetime(
                    self.env, shift.start_time, shift.tz, dt_format="medium"
                )
            else:
                shift.start_time_located = False

    @api.depends("tz", "end_time")
    def _compute_end_time_located(self):
        for shift in self:
            if shift.end_time:
                shift.end_time_located = format_datetime(
                    self.env, shift.end_time, shift.tz, dt_format="medium"
                )
            else:
                shift.end_time_located = False

    # Methods

    def _set_tz_context(self):
        """Set the timezone context for the shift."""
        self.ensure_one()
        return self.with_context(tz=self.tz)
