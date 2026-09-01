# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    nb_days_before_leave_end = fields.Integer(
        related="company_id.nb_days_before_leave_end",
        readonly=False,
    )
