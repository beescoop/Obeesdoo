# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductHazard(models.Model):
    _name = "product.hazard"
    _description = "product.hazard"

    name = fields.Char()
    type = fields.Selection([("fds", "FDS"), ("hazard", "Specific hazard")])
    active = fields.Boolean(default=True)
