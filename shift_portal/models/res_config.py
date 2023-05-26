# Copyright 2017-2020 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WebsiteShiftConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    min_percentage_presence = fields.Integer(
        string="Limit attendance percentage to define underpopulated shift",
        config_parameter="shift.min_percentage_presence",
    )
    min_hours_to_unsubscribe = fields.Integer(
        string="Minimum number of hours before a shift to unsubscribe",
        config_parameter="shift.min_hours_to_unsubscribe",
    )
    max_shift_per_day = fields.Integer(
        string="Maximum number of shifts per day for one cooperator",
        config_parameter="shift.max_shift_per_day",
    )
    max_shift_per_month = fields.Integer(
        string="Maximum number of shifts per month for one cooperator",
        config_parameter="shift.max_shift_per_month",
    )

    # Irregular worker settings
    highlight_rule_pc = fields.Integer(
        related="website_id.highlight_rule_pc", readonly=False
    )
    hide_rule = fields.Integer(related="website_id.hide_rule", readonly=False)
    irregular_enable_sign_up = fields.Boolean(
        related="website_id.irregular_enable_sign_up", readonly=False
    )
    irregular_past_shift_limit = fields.Integer(
        related="website_id.irregular_past_shift_limit", readonly=False
    )
    irregular_enable_unsubscribe = fields.Boolean(
        related="website_id.irregular_enable_unsubscribe", readonly=False
    )

    # Regular worker settings
    regular_past_shift_limit = fields.Integer(
        related="website_id.regular_past_shift_limit", readonly=False
    )
    regular_next_shift_limit = fields.Integer(
        string="Maximun number of next shift that will be shown",
        config_parameter="shift.regular_next_shift_limit",
    )
    regular_highlight_rule = fields.Integer(
        related="website_id.regular_highlight_rule", readonly=False
    )
    enable_subscribe_compensation = fields.Boolean(
        related="website_id.enable_subscribe_compensation", readonly=False
    )
    enable_unsubscribe_compensation = fields.Boolean(
        related="website_id.enable_unsubscribe_compensation", readonly=False
    )

    # General settings
    next_shifts_display_number = fields.Integer(
        string="Number of next shifts displayed on page 'My Shifts' by default",
        config_parameter="shift_portal.next_shifts_display_number",
    )
