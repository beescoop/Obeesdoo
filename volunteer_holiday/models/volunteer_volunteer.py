# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerVolunteer(models.Model):
    _inherit = "volunteer.volunteer"

    volunteer_leave_ids = fields.One2many(
        comodel_name="volunteer.volunteer.leave",
        inverse_name="volunteer_id",
        string="Leave",
    )
