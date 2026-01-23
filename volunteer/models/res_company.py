# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = ["res.company"]

    shift_nb_occurrence = fields.Integer(
        string="Number of shift occurrences",
        default=10,
    )

    _sql_constraints = [
        (
            "nb_occurrence_is_pos",
            "CHECK(shift_nb_occurrence > 0)",
            "The number of occurrence cannot be null or negative.",
        ),
    ]
