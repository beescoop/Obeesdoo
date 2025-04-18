# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ShiftCategory(models.Model):
    _name = "volunteer.shift.category"
    _description = "Shift Category"
    _order = "name"

    name = fields.Char(required=True)
    description = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
