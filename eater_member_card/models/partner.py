# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    @api.depends(
        "eater",  # cf comment hereunder
        "member_card_ids",
    )
    def _compute_bar_code(self):
        super()._compute_bar_code()

        eaters = self.filtered(lambda p: p.parent_eater_id)
        # warning : there is not constraint checking that parent_eater_id
        # is set if eater field is set to eater
        for partner in eaters:
            # Eaters must not have a barcode set. This should already be
            # implicitly true, but let's make it explicit.
            #
            # Eaters should use their parent's barcode.
            partner.barcode = False

    @api.multi
    def _new_eater(self, surname, name, email):
        partner = super()._new_eater(surname, name, email)
        partner.member_card_to_be_printed = True
        return partner
