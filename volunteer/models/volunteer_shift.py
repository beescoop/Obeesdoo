from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import format_datetime
from odoo.tools.translate import _

from odoo.addons.base.models.res_partner import _tz_get


class Shift(models.Model):
    _name = "volunteer.shift"
    _description = "Shift"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # General fields
    name = fields.Char(required=True)

    @api.model
    def _default_stage_id(self):
        Stage = self.env["volunteer.shift.stage"]
        return Stage.search([("state", "=", "draft")], limit=1)

    stage_id = fields.Many2one(
        "volunteer.shift.stage",
        default=_default_stage_id,
        copy=False,
        group_expand="_group_expand_stage_id",
    )

    state = fields.Selection(related="stage_id.state", store=True)
    max_volunteer_nb = fields.Integer("Max Volunteer", required=True)
    remaining_slots = fields.Integer(compute="_compute_remaining_slots")
    is_one_day = fields.Boolean(compute="_compute_is_one_day")

    # Date fields
    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        default=lambda self: self.env.user.tz or "UTC",
        required=True,
    )
    start_time = fields.Datetime(default=fields.datetime.now())
    start_time_located = fields.Char(compute="_compute_start_time_tz")
    end_time = fields.Datetime(default=fields.datetime.now())
    end_time_located = fields.Char(compute="_compute_end_time_tz")

    # Classification fields
    type_id = fields.Many2one("volunteer.shift.type", "Type", required=True)
    category_id = fields.Many2one("volunteer.shift.category", "Category")
    tag_ids = fields.Many2many("volunteer.shift.tag", string="Tags")

    # Relational fields
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    volunteer_participation_ids = fields.One2many(
        "volunteer.shift.participation", "shift_id", string="Participations"
    )
    coordinator_id = fields.Many2one("res.partner", "Coordinator")
    volunteer_ids = fields.One2many(
        "volunteer.shift.participation", "volunteer_id", string="Volunteers"
    )

    # Constrains
    @api.constrains("volunteer_participation_ids")
    def _unique_volunteer_participation(self):
        for shift in self:
            confirmed_volunteer = shift.volunteer_participation_ids.filtered(
                lambda participation: participation.registration_state == "confirmed"
            )
            confirmed_volunteer_ids = [
                participation.volunteer_id.id for participation in confirmed_volunteer
            ]

            if len(confirmed_volunteer_ids) != len(set(confirmed_volunteer_ids)):
                raise ValidationError(
                    _("A volunteer can only be registered once per shift.")
                )

    @api.constrains("max_volunteer_nb", "volunteer_participation_ids")
    def _check_max_volunteer_nb_higher_than_confirmed(self):
        """Check that the max number of volunteers is higher than the number of
        confirmed volunteers."""
        for shift in self:
            availability = shift.can_accept_participation()
            if not availability["can_accept"]:
                nb_confirmed_volunteers = availability["nb_confirmed_volunteers"]
                raise ValidationError(
                    _(
                        f"The maximum number of volunteers ({shift.max_volunteer_nb}) "
                        f"cannot be lower than the number "
                        f"of confirmed volunteers ({nb_confirmed_volunteers})."
                    )
                )

    _sql_constraints = [
        (
            "max_volunteer_nb_is_positive",
            "check (max_volunteer_nb > 0)",
            "The maximum of volunteers per shift cannot be null or negative.",
        ),
    ]

    # Computed fields
    @api.depends("tz", "start_time")
    def _compute_start_time_tz(self):
        for shift in self:
            if shift.start_time:
                shift.start_time_located = format_datetime(
                    self.env, shift.start_time, shift.tz, dt_format="medium"
                )
            else:
                shift.start_time = False

    @api.depends("tz", "start_time")
    def _compute_end_time_tz(self):
        for shift in self:
            if shift.end_time:
                shift.end_time_located = format_datetime(
                    self.env, shift.end_time, shift.tz, dt_format="medium"
                )
            else:
                shift.end_time = False

    @api.depends("volunteer_participation_ids")
    def _compute_remaining_slots(self):
        for shift in self:
            nb_confirmed_volunteers = len(
                shift.volunteer_participation_ids.filtered(
                    lambda participation: participation.registration_state
                    == "confirmed"
                )
            )
            shift.remaining_slots = shift.max_volunteer_nb - nb_confirmed_volunteers

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

    # Functions
    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    def _set_tz_context(self):
        """Set the timezone context for the shift."""
        self.ensure_one()
        return self.with_context(tz=self.tz)

    def can_accept_participation(self):
        """Check if the shift can accept more participations."""
        self.ensure_one()
        nb_confirmed_volunteers = len(
            self.volunteer_participation_ids.filtered(
                lambda participation: participation.registration_state == "confirmed"
            )
        )
        availability = {
            "can_accept": True,
            "nb_confirmed_volunteers": nb_confirmed_volunteers,
        }
        if self.max_volunteer_nb < nb_confirmed_volunteers:
            availability["can_accept"] = False
        return availability
