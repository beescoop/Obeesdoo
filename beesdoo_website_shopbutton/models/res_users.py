# Copyright 2025 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Users(models.Model):
    _inherit = "res.users"

    webshop_url = fields.Char(
        read_only=True,
        invisible=True,
        compute="_compute_webshop_url",
        help="The URL of the webshop for this user.",
    )

    def _compute_webshop_url(self):
        for user in self:
            partner = user.partner_id
            email = partner.email
            coop = partner.cooperator_register_number
            first_name = partner.name.split()[0] if partner.name else False
            last_name = partner.name.split()[-1] if partner.name else False
            if not email or not coop or not first_name or not last_name:
                user.webshop_url = False
            else:
                user.webshop_url = (
                    f"https://webshop.bees-coop.be/?email={email}&coop={coop}"
                    f"&FirstName={first_name}&LastName={last_name}"
                )
