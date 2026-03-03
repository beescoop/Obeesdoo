# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerVolunteerLeaveType(models.Model):
    _name = "volunteer.volunteer.leave.type"
    _description = "Volunteer Leave"
    _order = "name"

    name = fields.Char(string="Leave Type", required="True")
    description = fields.Char()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
