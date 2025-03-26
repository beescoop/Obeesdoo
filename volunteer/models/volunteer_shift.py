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
    max_volunteer_nb = fields.Integer("Max Volunteer", default=1, required=True)

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
    coordinator_ids = fields.One2many(
        "volunteer.shift.participation", "volunteer_id", string="Coordinators"
    )
    volunteer_ids = fields.One2many(
        "volunteer.shift.participation", "volunteer_id", string="Volunteers"
    )

    # Constrains
    @api.constrains("volunteer_participation_ids")
    def _check_remaining_slots(self):
        for shift in self:
            nb_confirmed_volunteers = len(
                shift.volunteer_participation_ids.filtered(
                    lambda participation: participation.registration_state
                    == "confirmed"
                )
            )
            if nb_confirmed_volunteers > shift.max_volunteer_nb:
                raise ValidationError(
                    _(
                        f"It is not possible to register"
                        f" {nb_confirmed_volunteers} volunteers in this shift."
                        f" The maximum capacity is {shift.max_volunteer_nb}"
                    )
                )

    # _sql_constraints = [
    # (
    #     "volunteer_unique",
    #     "unique (volunteer_id, shift_id)",
    #     "Test",
    # )]

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

    @api.model
    def _group_expand_stage_id(self, stages, domain, order):
        return stages.search([], order=order)
