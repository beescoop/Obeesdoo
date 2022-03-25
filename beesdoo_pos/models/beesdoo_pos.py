from odoo import api, models


class BeescoopPosPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def get_eater(self):
        self.ensure_one()
        eaters = []
        # todo check for max eater
        for eater in self.child_eater_ids:
            eaters.append(eater.name)
        return eaters
