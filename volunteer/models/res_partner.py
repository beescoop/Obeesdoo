# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = ["res.partner"]

    volunteer_ids = fields.One2many(
        comodel_name="volunteer.volunteer",
        inverse_name="partner_id",
        string="Volunteer",
    )
