# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftRuleMixin(models.AbstractModel):
    _name = "volunteer.shift.rule.mixin"
    _description = "volunteer Shift Rule Mixin"

    sequence = fields.Integer()
    description = fields.Char()
    required_number = fields.Integer(
        string="How many ?",
        required=True,
    )
