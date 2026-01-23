# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from random import randint

from odoo import fields, models


class VolunteerShiftTag(models.Model):
    _name = "volunteer.shift.tag"
    _description = "Shift Tag"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Char(tracking=True)

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(default=_get_default_color, tracking=True)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
        tracking=True,
    )

    # SQL Constraints

    _sql_constraints = [
        (
            "name_company_uniq",
            "UNIQUE(name, company_id)",
            "Tag with such name already exists in the company!",
        ),
        (
            "name_nocompany_uniq",
            "EXCLUDE(name WITH =) WHERE(company_id IS NULL)",
            "Shared tag with such name already exists!",
        ),
    ]
