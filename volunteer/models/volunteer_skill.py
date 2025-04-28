# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerSkill(models.Model):
    _name = "volunteer.skill"
    _description = "Volunteer Skills"

    name = fields.Char()
    description = fields.Char()
    category_id = fields.Many2one(
        comodel_name="volunteer.skill.category",
        string="Category",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    def name_get(self):
        res = []
        for record in self:
            if record.category_id:
                name = f"{record.category_id.name}: {record.name}"
            else:
                name = f"{record.name}"
            res.append((record.id, name))
        return res
