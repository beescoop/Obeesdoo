# -*- coding: utf-8 -*-
from openerp import models, fields, api

class NewMemberCardWizard(models.TransientModel):
    """
        A transient model for the creation of a new card.
        The user can only define the raison why a new card is
        needed and the eater/worker that is concerned.
    """
    _name = 'membercard.new.wizard'

    def _get_default_partner(self):
        return self.env.context['active_id']

    new_comment = fields.Text('Reason', required=True)
    partner_id = fields.Many2one('res.partner', default=_get_default_partner)

    @api.one
    def create_new_card(self):
        client = self.partner_id.sudo()
        client._deactivate_active_cards()
        client._new_card(self.new_comment, self.env.uid)
