# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one("beesdoo.product.label", domain=[("type", "=", "eco")])
    local_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "local")]
    )
    fair_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "fair")]
    )
    origin_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "delivery")]
    )

    display_unit = fields.Many2one("uom.uom")
    default_reference_unit = fields.Many2one("uom.uom")
    display_weight = fields.Float(
        compute="_compute_display_weight",
        store=True,
        digits="Stock Weight",
    )

    note = fields.Text("Comments", copy=False)

    @api.depends("weight", "display_unit")
    def _compute_display_weight(self):
        for product in self:
            product.display_weight = product.weight * product.display_unit.factor

    @api.constrains("display_unit", "default_reference_unit")
    def _unit_same_category(self):
        for product in self:
            if (
                product.display_unit.category_id
                != product.default_reference_unit.category_id
            ):
                raise UserError(
                    _(
                        "Reference Unit and Display Unit should belong to the "
                        "same category "
                    )
                )
