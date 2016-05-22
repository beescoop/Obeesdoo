# -*- coding: utf-8 -*-
from openerp import models, fields, api

class RequestMemberCardPrintingWizard(models.TransientModel):

    _name = 'membercard.requestprinting.wizard'

    def _get_selected_partners(self):
        return self.env.context['active_ids']

    partner_ids = fields.Many2many('res.partner', default=_get_selected_partners)


    @api.one
    def request_printing(self):
        for client in self.partner_ids:
            client._request_membercard_printing()
