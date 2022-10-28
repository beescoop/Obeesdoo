# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.depends(
        "parent_eater_id",
        "parent_eater_id.barcode",
        "eater",  # cf comment hereunder
        "member_card_ids",
    )
    def _compute_bar_code(self):
        parents = self.filtered(lambda p: not p.parent_eater_id)
        eaters = self.filtered(lambda p: p.parent_eater_id)
        super(Partner, parents)._compute_bar_code()

        # warning : there is not constraint checking that parent_eater_id
        # is set if eater field is set to eater
        for partner in eaters:
            partner.barcode = partner.parent_eater_id.barcode

    @api.multi
    def _new_eater(self, surname, name, email):
        partner = super()._new_eater(surname, name, email)
        partner.member_card_to_be_printed = True
        return partner
