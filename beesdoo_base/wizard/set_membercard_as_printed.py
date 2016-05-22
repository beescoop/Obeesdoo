# -*- coding: utf-8 -*-
from openerp import models, fields, api

class RequestMemberCardPrintingWizard(models.TransientModel):

    _name = 'membercard.set_as_printed.wizard'

    def _get_selected_partners(self):
        return self.env.context['active_ids']

    partner_ids = fields.Many2many('res.partner', default=_get_selected_partners)


    @api.one
    def set_as_printed(self):
        for client in self.partner_ids:
            client._set_membercard_as_printed()
