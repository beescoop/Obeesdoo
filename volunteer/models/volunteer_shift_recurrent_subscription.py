# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftRecurrentSubscription(models.Model):
    _name = "volunteer.shift.recurrent.subscription"
    _description = "Shift Recurrent Subscription"
    _order = "start_date"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]

    # Date fields

    start_date = fields.Date(
        required=True, tracking=True, default=lambda self: fields.Date.today()
    )
    end_date = fields.Date(tracking=True)

    # Relational fields

    volunteer_id = fields.Many2one(
        comodel_name="volunteer.volunteer",
        string="Volunteer",
        required=True,
        tracking=True,
    )
    generator_id = fields.Many2one(
        comodel_name="volunteer.shift.recurrent.generator",
        string="Shift Generator",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="generator_id.company_id",
        store=True,
        readonly=True,
    )
