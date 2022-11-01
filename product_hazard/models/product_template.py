# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fds_label = fields.Many2one(
        "product.hazard",
        string="FDS label",
        domain=[("type", "=", "fds")],
        translate=True,
    )
    hazard_label = fields.Many2one(
        "product.hazard",
        string="Hazard label",
        domain=[("type", "=", "hazard")],
        translate=True,
    )
