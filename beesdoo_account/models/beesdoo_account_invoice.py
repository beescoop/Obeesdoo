# -*- coding: utf-8 -*-
'''
 Created on 5 déc. 2015

 @author: Thibault François
'''

from openerp import models, fields, api

class BeesdooAccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    date_invoice = fields.Date(required=True)