from odoo import api, models


class BeescoopPosPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def get_eater(self):
        eaters = [False] * self._get_max_nb_eater_allowed()
        for i, eater in enumerate(self.child_eater_ids):
            eaters[i] = eater.name
        return eaters

    def _get_max_nb_eater_allowed(self):
        if self.eater == "eater":
            max_nb_eater_allowed = (
                self.parent_eater_id._cooperator_share_type().max_nb_eater_allowed
            )
        else:
            max_nb_eater_allowed = (
                self._cooperator_share_type().max_nb_eater_allowed
            )
        return max_nb_eater_allowed
