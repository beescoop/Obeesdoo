# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class Partner(models.Model):
    _inherit = ["res.partner"]

    volunteer_ids = fields.One2many(
        "volunteer.volunteer", "partner_id", string="Volunteer"
    )
