# -*- coding: utf-8 -*-
from openerp import models, fields

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