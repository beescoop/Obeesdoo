from odoo import api, models


class BeescoopPosPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def get_eater(self):
        self.ensure_one()
        # todo check for max eater
        return [eater.name for eater in self.child_eater_ids]
