# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_solidarity = fields.Boolean(
        string="Activate solidarity offers and requests",
        config_parameter="shift_solidarity.enable_solidarity",
    )
    solidarity_counter_start_value = fields.Integer(
        string="Start value of the global solidarity counter",
        config_parameter="shift_solidarity.solidarity_counter_start_value",
        default=0,
    )
    solidarity_counter_limit = fields.Integer(
        string="Limit value of the global solidarity counter",
        config_parameter="shift_solidarity.solidarity_counter_limit",
        default=0,
    )
    max_solidarity_requests_number = fields.Integer(
        string="Max number of solidarity requests per year",
        config_parameter="shift_solidarity.max_solidarity_requests_number",
    )
