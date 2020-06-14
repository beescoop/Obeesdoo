from odoo import api, models


class BeescoopPosPartner(models.Model):
    _inherit = "res.partner"

    def _get_eater(self):
        eaters = [False, False, False]
        for i, eater in enumerate(self.child_eater_ids):
            eaters[i] = eater.name
        return tuple(eaters)

    @api.multi
    def get_eater(self):
        eater1, eater2, eater3 = self._get_eater()
        return eater1, eater2, eater3
