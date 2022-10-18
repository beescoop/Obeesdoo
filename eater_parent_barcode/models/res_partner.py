# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    parent_barcode = fields.Char(
        compute="_compute_bar_code", string="Parent Barcode", store=True
    )

    @api.multi
    @api.depends(
        "parent_eater_id",
        "parent_eater_id.barcode",
        "eater",
        "member_card_ids",
    )
    def _compute_bar_code(self):
        super()._compute_bar_code()
        for partner in self:
            if partner.parent_eater_id:
                partner.parent_barcode = partner.parent_eater_id.barcode
