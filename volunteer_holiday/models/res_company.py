# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ["res.company"]

    nb_days_before_leave_end = fields.Integer(
        string="Number of days for notification before end of leave",
        default=7,
    )

    _sql_constraints = [
        (
            "nb_days_is_pos",
            "check (nb_days_before_leave_end > 0)",
            "The number of days cannot be null or negative.",
        ),
    ]
