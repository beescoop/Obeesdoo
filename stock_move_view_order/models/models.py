#coding:utf-8

from odoo import models, fields, api

class StockMoveViewOrder(models.Model):
    _inherit = "stock.move.line"

