from odoo import models, fields, api

class NewMemberCardWizard(models.TransientModel):
    """
        A transient model for the creation of a new card.
        The user can only define the raison why a new card is
        needed and the eater/worker that is concerned.
    """
    _name = 'membercard.new.wizard'

    def _get_default_partner(self):
        return self.env.context['active_id']

    new_comment = fields.Char('Reason', required=True)
    partner_id = fields.Many2one('res.partner', default=_get_default_partner)
    force_barcode = fields.Char('Force Barcode', groups="beesdoo_base.group_force_barcode")

    @api.one
    def create_new_card(self):
        client = self.partner_id.sudo()
        client._deactivate_active_cards()
        client._new_card(self.new_comment, self.env.uid, barcode=self.force_barcode)
        client.member_card_to_be_printed = True

class RequestMemberCardPrintingWizard(models.TransientModel):

    _name = 'membercard.requestprinting.wizard'

    def _get_selected_partners(self):
        return self.env.context['active_ids']

    partner_ids = fields.Many2many('res.partner', default=_get_selected_partners)


    @api.one
    def request_printing(self):
        self.partner_ids.write({'member_card_to_be_printed' : True})

class SetAsPrintedWizard(models.TransientModel):

    _name = 'membercard.set_as_printed.wizard'

    def _get_selected_partners(self):
        return self.env.context['active_ids']

    partner_ids = fields.Many2many('res.partner', default=_get_selected_partners)

    @api.one
    def set_as_printed(self):
        self.partner_ids.write({'member_card_to_be_printed' : False,
                                'last_printed' : fields.Datetime.now()})
