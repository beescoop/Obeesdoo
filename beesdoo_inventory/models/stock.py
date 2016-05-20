# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    max_shipping_date = fields.Datetime("End Shipping Date")
    responsible = fields.Many2one("res.partner", string="Responsible Person")
