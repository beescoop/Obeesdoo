# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class Volunteer(models.Model):
    _name = "volunteer.volunteer"
    _description = "Volunteer"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    shift_participation_ids = fields.One2many(
        "volunteer.shift.participation", "volunteer_id", "participation"
    )

    is_regular = fields.Boolean(
        default=False,
        readonly=True,
        help="Is regular if registered for at least one recurrent shift",
    )
