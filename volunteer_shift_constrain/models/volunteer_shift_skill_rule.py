# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftSkillRule(models.Model):
    _name = "volunteer.shift.skill.rule"
    _description = "Volunteer Shift Skill Rule"
    _inherit = [
        "volunteer.shift.rule.mixin",
    ]

    skill_id = fields.Many2one(
        comodel_name="volunteer.skill",
        string="Skill",
    )
    shift_constrain_id = fields.Many2one(
        string="Shift Constrain",
        comodel_name="volunteer.shift.constrain",
        required=True,
    )
