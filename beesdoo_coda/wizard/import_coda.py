# -*- coding: utf-8 -*-
'''
Created on 16 mai 2016

@author: Thibault Francois (thibault@françois.be)
'''

from coda.parser import Parser, CodaParserException
from openerp import models, _

class CodaBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _generate_note(self, move):
        notes = []
        if move.counterparty_name:
            notes.append("%s: %s" % (_('Counter Party Name'), move.counterparty_name))
        if move.counterparty_address:
            notes.append("%s: %s" % (_('Counter Party Address'), move.counterparty_address))
        if move.counterparty_number:
            notes.append("%s: %s" % (_('Counter Party Account'), move.counterparty_number))
        if move.communication:
            notes.append("%s: %s" % (_('Communication'), move.communication))
        return '\n'.join(notes)

    def _get_move_value(self, move, statement, sequence):
        move_data = {
            'name': move.communication, #ok
            'note': self._generate_note(move),
            'date': move.entry_date, #ok
            'amount': move.transaction_amount if move.transaction_amount_sign == '0' else - move.transaction_amount, #ok
            'account_number': move.counterparty_number, #ok
            'partner_name': move.counterparty_name, #ok
            'ref': move.ref,
            'sequence': sequence, #ok
            'unique_import_id' : statement.coda_seq_number + '-' + statement.old_balance_date + '-' + statement.new_balance_date + '-' +  move.ref
        }
        return move_data

    def _get_statement_data(self, statement):
        statement_data = {
            'name' : statement.paper_seq_number,
            'date' : statement.creation_date,
            'balance_start': statement.old_balance, #ok
            'balance_end_real' : statement.new_balance, #ok
            'coda_note' : '',
            'transactions' : []
        }
        return statement_data
    
    def _get_acc_number(self, acc_number):
        #Check if we match the exact acc_number or the end of an acc number
        journal = self.env['account.journal'].search([('bank_acc_number', '=like', '%' + acc_number)])
        if not journal or len(journal) > 1: #if not found or ambiguious 
            return acc_number
        
        return journal.bank_acc_number

    def _parse_file(self, data_file):
        parser = Parser()
        try:
            statements = parser.parse(data_file)
        except CodaParserException:
            return super(CodaBankStatementImport, self)._parse_file(data_file)
        currency_code = False
        account_number = False

        stmts_vals = []
        for statement in statements:
            account_number =  statement.acc_number
            currency_code = statement.currency
            statement_data = self._get_statement_data(statement)
            stmts_vals.append(statement_data)
            for move in statement.movements:
                statement_data['transactions'].append(self._get_move_value(move, statement, len(statement_data['transactions']) + 1))

        return currency_code, self._get_acc_number(account_number), stmts_vals
