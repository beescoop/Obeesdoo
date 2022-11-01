# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    scale_label_info_1 = fields.Char(string="Scale label info 1")
    scale_label_info_2 = fields.Char(string="Scale label info 2")
    scale_sale_unit = fields.Char(
        compute="_compute_scale_sale_uom", string="Scale sale unit", store=True
    )
    scale_category = fields.Many2one("scale.category", string="Scale Category")
    scale_category_code = fields.Integer(
        related="scale_category.code",
        string="Scale category code",
        readonly=True,
        store=True,
    )

    @api.depends("uom_id", "uom_id.category_id", "uom_id.category_id.type")
    @api.multi
    def _compute_scale_sale_uom(self):
        for product in self:
            if product.uom_id.category_id.type == "unit":
                product.scale_sale_unit = "F"
            elif product.uom_id.category_id.type == "weight":
                product.scale_sale_unit = "P"
