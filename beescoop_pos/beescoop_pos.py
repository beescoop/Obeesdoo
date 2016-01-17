# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.fields import One2many, Float, Many2one

class BeesPOS(models.Model):
    _inherit = 'pos.config'
    
    bill_value = One2many('bill_value', 'pos')
    
class BillValue(models.Model):
    _name = 'bill_value'
    _order = 'name asc'
    
    name = fields.Float(string='Name')
    pos = Many2one('pos.config')
    
class BeesAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.cashbox'
    
    def _get_default_line(self):
        print "in _get_default_line", self.env.context['active_id']
        if not self.env.context.get('active_id'):
            return []
        
        default_lines = []
        pos_obj = self.env['pos.session']
        pos_session_rec = pos_obj.browse(self.env.context['active_id'])
        for bill_value_rec in pos_session_rec.config_id.bill_value:
            default_lines.append((0, 0, {'coin_value' : bill_value_rec.name}))        
        return default_lines
    
    cashbox_lines_ids = fields.One2many(default=_get_default_line)