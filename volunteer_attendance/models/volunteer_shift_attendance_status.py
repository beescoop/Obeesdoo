# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftAttendanceStatus(models.Model):
    _name = "volunteer.shift.attendance.status"
    _description = "Specify status of a volunteer's attendance to a shift"
    _order = "name"

    name = fields.Char(
        required=True,
    )
    description = fields.Char()

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )

    # SQL Constraints

    _sql_constraints = [
        (
            "name_company_uniq",
            "UNIQUE (name, company_id)",
            "Category with such name already exists in the company!",
        ),
        (
            "name_nocompany_uniq",
            "EXCLUDE (name WITH =) WHERE (company_id IS NULL)",
            "Shared category with such name already exists!",
        ),
    ]
