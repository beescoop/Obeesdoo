# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerVolunteerLeave(models.Model):
    _name = "volunteer.volunteer.leave"
    _description = "Volunteer Leave"

    # Fields

    volunteer_id = fields.Many2one(
        comodel_name="volunteer.volunteer",
        string="Volunteer",
        required=True,
    )
    start_date = fields.Date(
        required=True,
    )
    end_date = fields.Date(
        required=True,
    )
    type_id = fields.Many2one(
        comodel_name="volunteer.volunteer.leave.type",
        string="Leave Type",
        required="True",
    )
