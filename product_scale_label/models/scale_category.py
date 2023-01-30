# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ScaleCategory(models.Model):
    _name = "scale.category"
    _description = "scale.category"

    name = fields.Char(string="Scale name category")
    code = fields.Integer(string="Category code")

    _sql_constraints = [
        (
            "code_scale_categ_uniq",
            "unique (code)",
            "The code of the scale category must be unique !",
        )
    ]
