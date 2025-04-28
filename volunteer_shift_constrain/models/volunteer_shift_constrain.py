# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ShiftConstrain(models.Model):
    _name = "volunteer.shift.constrain"
    _description = "Shift Constrain"

    name = fields.Char(required=True)
    description = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
    )
    skill_category_rule_ids = fields.One2many(
        comodel_name="volunteer.shift.skill.category.rule",
        inverse_name="shift_constrain_id",
        string="Skill Category Constrains",
    )
    skill_rule_ids = fields.One2many(
        comodel_name="volunteer.shift.skill.rule",
        inverse_name="shift_constrain_id",
        string="Skill Constrains",
    )

    # Reverse fields
    shift_type_ids = fields.Many2many(
        comodel_name="volunteer.shift.type",
        string="Shift Types",
    )
    shift_ids = fields.Many2many(
        comodel_name="volunteer.shift",
        string="Shifts",
    )
