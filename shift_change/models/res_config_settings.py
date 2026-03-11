# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    old_shift_hour_limit_change = fields.Integer(
        config_parameter="shift_change.hour_limit_change",
    )
    new_shift_hour_limit_change = fields.Integer(
        config_parameter="shift_change.hour_limit_change",
    )
    same_shift_change_max = fields.Integer(
        config_parameter="shift_change.same_shift_change_max",
    )
