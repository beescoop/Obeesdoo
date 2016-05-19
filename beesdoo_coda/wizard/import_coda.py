# -*- coding: utf-8 -*-
'''
Created on 16 mai 2016

@author: Thibault Francois (thibault@françois.be)
'''

from coda.parser import Parser
from openerp import models, fields, api
# parser = Parser()
# print "salut"
# 
# with open("example.coda") as f:
#     content = f.read()
#     
# print content
# statements = parser.parse(content)
# import pdb; pdb.set_trace()


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'
    
    def _parse_file(self, data_file):
        currency_code = False
        account_number = '0'
        stmts_vals = [{
            'name': '',
            'date': '',
            'balance_start': '',
            'balance_end_real' : '',
            'transactions' : [
                {            
                    'name': '',
                    'note': '',
                    'date': '',
                    'amount': '',
                    'account_number': '',
                    'partner_name': '',
                    'ref': '',
                    'sequence': '',
                    'unique_import_id' : ''
                }
            ],
        }]
        return currency_code, account_number, stmts_vals