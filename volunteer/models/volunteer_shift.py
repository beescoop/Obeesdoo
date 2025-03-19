import pytz

from odoo import api, fields, models
from odoo.tools.safe_eval import datetime


class Shift(models.Model):
    _name = "volunteer.shift"
    _description = "Shift"
    name = fields.Char(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("canceled", "Canceled")],
        default="draft",
    )
    start_time = fields.Datetime(default=fields.datetime.now())
    end_time = fields.Datetime(default=fields.datetime.now())
    tz = fields.Selection("_tz_get", default=lambda self: self.env.user.tz)
    max_volunteer_nb = fields.Integer("Max Volunteer", default=1)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    type_id = fields.Many2one("volunteer.shift.type", "Type", required=True)
    category_id = fields.Many2one("volunteer.shift.category", "Category")
    tag_ids = fields.Many2many("volunteer.shift.tag", string="Tags")

    @api.model
    def _tz_get(self):
        return [(tz, tz) for tz in pytz.all_timezones]

    def button_confirm_shift(self):
        for shift in self:
            shift.state = "confirmed"
        return True

    def button_cancel_shift(self):
        for shift in self:
            shift.state = "canceled"
        return True


def _convert_naive_to_str_aware_date(naive_date, timezone, fmt):
    aware_date = naive_date.astimezone(pytz.timezone(timezone))
    return datetime.datetime.strftime(aware_date, fmt)

    ###########################################
    #       Computed field name               #
    #       Work in Progress for addition     #
    #       in a future another modules       #
    ###########################################

    # name = fields.Char(compute="_compute_name", inverse="_inverse_name",
    #                                               store=True, required=True)
    # def _inverse_name(self):
    #     for record in self:
    #         pass
    #     return True
    # @api.depends("category_id", "type_id", "start_time", "end_time")
    # def _compute_name(self):
    #     pattern = "^\d{4}\/\d{2}\/\d{2}[_]\d{2}:\d{2}-\d{4}\/\d{2}\/\d{2}_\d{2}:\d{2}.*"
    #     for record in self:
    #         shift_category = record.category_id.name
    #         shift_type = record.type_id.name
    #         start_date = _convert_naive_to_str_aware_date(
    #             record.start_time, record.timezone, "%Y/%m/%d_%H:%M"
    #         )
    #         end_date = _convert_naive_to_str_aware_date(
    #             record.end_time, record.timezone, "%Y/%m/%d_%H:%M"
    #         )
    #         if shift_type is False and shift_category is False:
    #             computed_name = f"{start_date}-{end_date}"
    #         elif shift_category is False:
    #             computed_name = f"{start_date}-{end_date}_{shift_type}"
    #         elif shift_type is False:
    #             computed_name = f"{start_date}-{end_date}_{shift_category}"
    #         else:
    #             computed_name = f"{start_date}-{end_date}_{shift_category}_{shift_type}"
    #
    #         if (record.name == False or record.name is "") or
    #                                   re.match(pattern,record.name) != None:
    #             record.name = computed_name
    #     return True
