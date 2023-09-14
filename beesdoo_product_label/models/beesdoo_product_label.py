# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"
    _description = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection(
        [
            ("eco", "Écologique"),
            ("local", "Local"),
            ("fair", "Équitable"),
            ("delivery", "Distribution"),
        ]
    )
    color_code = fields.Char()
    logo = fields.Binary()
    active = fields.Boolean(default=True)
