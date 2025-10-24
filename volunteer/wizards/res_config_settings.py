# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_nb_occurrence = fields.Integer(
        related="company_id.shift_nb_occurrence",
        readonly=False,
    )
