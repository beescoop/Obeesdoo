# Copyright 2019-2020 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session", default=False
    )
