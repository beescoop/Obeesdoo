# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class BeesPOS(models.Model):
    _inherit = 'pos.config'

    bill_value = fields.One2many('bill_value', 'pos')

class BillValue(models.Model):
    _name = 'bill_value'
    _order = 'name asc'

    name = fields.Float(string='Name')
    pos = fields.Many2one('pos.config')

class BeesAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.cashbox'

    def _get_default_line(self):
        if not self.env.context.get('active_id'):
            return []

        pos_session_rec = self.env['pos.session'].browse(self.env.context['active_id'])
        return [(0, 0, {'coin_value' : bill_value_rec.name}) for bill_value_rec in pos_session_rec.config_id.bill_value]

    cashbox_lines_ids = fields.One2many(default=_get_default_line)

class BeescoopPosOrder(models.Model):

    _inherit = 'pos.order'

    @api.model
    def send_order(self, receipt_name):
        order = self.search([('pos_reference', '=', receipt_name)])
        if not order:
            return _('Error: no order found')
        if not order.partner_id.email:
            return _('Cannot send the ticket, no email address found on the client')
        mail_template = self.env.ref("beescoop_pos.email_send_ticket")
        mail_template.send_mail(order.id)
        return _("Ticket sent")