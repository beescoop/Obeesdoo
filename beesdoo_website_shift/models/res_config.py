# Copyright 2017-2020 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WebsiteShiftConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

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

    # Regular worker settings
    regular_past_shift_limit = fields.Integer(
        related="website_id.regular_past_shift_limit", readonly=False
    )
    regular_next_shift_limit = fields.Integer(
        related="website_id.regular_next_shift_limit", readonly=False
    )
    regular_highlight_rule = fields.Integer(
        related="website_id.regular_highlight_rule", readonly=False
    )
