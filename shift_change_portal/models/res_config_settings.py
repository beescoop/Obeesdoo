# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # enable change in portal
    enable_shift_changes = fields.Boolean(
        string="Activate shift changes",
        config_parameter="shift_change_portal.enable_shift_change",
    )
