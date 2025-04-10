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
    max_volunteer_nb = fields.Integer("Max Volunteer", required=True)
    remaining_slots = fields.Integer(compute="_compute_remaining_slots")
    is_one_day = fields.Boolean(compute="_compute_is_one_day")

    # Stage fields

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

    # Date fields

    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        default=lambda self: self.env.user.tz or "UTC",
        required=True,
    )
    start_time = fields.Datetime(default=fields.datetime.now())
    start_time_located = fields.Char(compute="_compute_start_time_located")
    end_time = fields.Datetime(default=fields.datetime.now())
    end_time_located = fields.Char(compute="_compute_end_time_located")

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
        "volunteer.shift.participation", "shift_id", string="Participation"
    )
    coordinator_id = fields.Many2one("res.partner", "Coordinator")
    volunteer_ids = fields.One2many(
        "volunteer.volunteer", compute="_compute_volunteer_ids", string="Volunteers"
    )

    # Constrains

    @api.constrains("volunteer_participation_ids")
    def _unique_volunteer_participation(self):
        """Check that a volunteer can only be registered once per shift."""

        for shift in self:
            confirmed_participation = shift.get_booking_status()[
                "confirmed_participation"
            ]
            confirmed_volunteer_ids = [
                participation.volunteer_id.id
                for participation in confirmed_participation
            ]

            if len(confirmed_volunteer_ids) != len(set(confirmed_volunteer_ids)):
                raise ValidationError(
                    _("A volunteer can only be registered once per shift.")
                )

    @api.constrains("max_volunteer_nb", "volunteer_participation_ids")
    def _check_can_accept_new_participation(self):
        for shift in self:
            booking_status = shift.get_booking_status()
            if not booking_status["can_accept_participation"]:
                nb_confirmed_participation = booking_status[
                    "nb_confirmed_participation"
                ]
                raise ValidationError(
                    _(
                        f"The maximum number of volunteers ({shift.max_volunteer_nb}) "
                        f"cannot be lower than the number "
                        f"of confirmed volunteers ({nb_confirmed_participation})."
                    )
                )

    _sql_constraints = [
        (
            "max_volunteer_nb_is_positive",
            "check (max_volunteer_nb > 0)",
            "The maximum of volunteers per shift cannot be null or negative.",
        ),
    ]

    # Compute Methods

    @api.depends("volunteer_participation_ids")
    def _compute_volunteer_ids(self):
        for shift in self:
            booking_status = shift.get_booking_status()
            if shift.volunteer_participation_ids:
                shift.volunteer_ids = booking_status["confirmed_participation"].mapped(
                    "volunteer_id"
                )
            else:
                shift.volunteer_ids = False

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

    @api.depends("volunteer_participation_ids")
    def _compute_remaining_slots(self):
        for shift in self:
            nb_confirmed_participation = shift.get_booking_status()[
                "nb_confirmed_participation"
            ]
            shift.remaining_slots = shift.max_volunteer_nb - nb_confirmed_participation

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

    # Methods

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)

    def _set_tz_context(self):
        """Set the timezone context for the shift."""

        self.ensure_one()
        return self.with_context(tz=self.tz)

    def get_booking_status(self):
        """Get the shift booking status by returning a dictionary of :
        - can_accept_participation: boolean
        - confirmed_participation: recordset of confirmed participation
        - nb_confirmed_participation: number of confirmed participation
        """

        self.ensure_one()
        confirmed_participation = self.volunteer_participation_ids.filtered(
            lambda participation: participation.registration_state == "confirmed"
        )
        nb_confirmed_participation = len(confirmed_participation)
        booking_status = {
            "can_accept_participation": True,
            "confirmed_participation": confirmed_participation,
            "nb_confirmed_participation": nb_confirmed_participation,
        }
        if self.max_volunteer_nb < nb_confirmed_participation:
            booking_status["can_accept_participation"] = False
        return booking_status
