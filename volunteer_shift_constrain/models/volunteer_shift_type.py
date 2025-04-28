# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ShiftType(models.Model):
    _inherit = "volunteer.shift.type"

    shift_constrain_id = fields.Many2one(
        string="Constrain",
        comodel_name="volunteer.shift.constrain",
    )
