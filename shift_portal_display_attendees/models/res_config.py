# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class WebsiteShiftConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    display_attendees_on_portal = fields.Boolean(
        related="website_id.display_attendees_on_portal", readonly=False
    )
