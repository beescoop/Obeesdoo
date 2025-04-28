# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftSkillCategoryRule(models.Model):
    _name = "volunteer.shift.skill.category.rule"
    _description = "Volunteer Shift Skill Category Rule"
    _inherit = [
        "volunteer.shift.rule.mixin",
    ]

    skill_category_id = fields.Many2one(
        comodel_name="volunteer.skill.category",
        string="Skill Category",
    )
    shift_constrain_id = fields.Many2one(
        string="Shift Constrain",
        comodel_name="volunteer.shift.constrain",
        required=True,
    )
