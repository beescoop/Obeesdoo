# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    webshop_url = fields.Char(
        compute="_compute_webshop_url",
        help="The URL of the webshop for this user.",
    )

    def _compute_webshop_url(self):
        for user in self:
            partner = user.partner_id
            email = partner.email
            coop_number = partner.cooperator_register_number
            first_name = partner.firstname or ""
            last_name = partner.lastname or ""
            if not email or not coop_number:
                user.webshop_url = False
            else:
                user.webshop_url = (
                    f"https://webshop.bees-coop.be/?email={email}"
                    f"&coop={coop_number}&FirstName={first_name}"
                    f"&LastName={last_name}"
                )
