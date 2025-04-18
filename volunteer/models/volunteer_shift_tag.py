# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from random import randint

from odoo import fields, models


class ShiftTag(models.Model):
    _name = "volunteer.shift.tag"
    _description = "Shift Tag"
    _order = "name"

    name = fields.Char(required=True)
    description = fields.Char()

    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer(default=_get_default_color)

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
