# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    display_attendees_on_portal = fields.Boolean(
        default=True,
        help="Display names of registered attendees on shift "
        "subscription modals in the portal",
    )
