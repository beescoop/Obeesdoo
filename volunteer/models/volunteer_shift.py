from odoo import api, fields, models
from odoo.tools import format_datetime

from odoo.addons.base.models.res_partner import _tz_get


class Shift(models.Model):
    _name = "volunteer.shift"
    _description = "Shift"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("canceled", "Canceled")],
        default="draft",
    )
    max_volunteer_nb = fields.Integer("Max Volunteer", default=1)
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
