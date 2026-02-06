# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    hour_limit_change = fields.Integer(
        string="Number of hours above which a cooperator cannot change his shift",
        config_parameter="shift_change.hour_limit_change",
    )
    same_shift_change_max = fields.Integer(
        string="Number of time the same shift can be changed",
        config_parameter="shift_change.same_shift_change_max",
    )
