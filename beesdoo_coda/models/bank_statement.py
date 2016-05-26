# -*- coding: utf-8 -*-
'''
Created on 16 mai 2016

@author: Thibault Francois (thibault@françois.be)
'''
from openerp import models, fields

class BankStatement(models.Model):
    _inherit = 'account.bank.statement'

    coda_note = fields.Text()
