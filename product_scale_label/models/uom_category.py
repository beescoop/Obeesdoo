# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UOMCategory(models.Model):
    _inherit = "uom.category"

    type = fields.Selection(
        [
            ("unit", "Unit"),
            ("weight", "Weight"),
            ("time", "Time"),
            ("distance", "Distance"),
            ("surface", "Surface"),
            ("volume", "Volume"),
            ("other", "Other"),
        ],
        string="Category type",
        default="unit",
    )
