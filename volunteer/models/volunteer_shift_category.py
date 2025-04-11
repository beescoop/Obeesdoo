# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ShiftCategory(models.Model):
    _name = "volunteer.shift.category"
    _description = "Shift Category"

    name = fields.Char()
    description = fields.Char()
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
