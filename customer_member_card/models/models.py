#coding:utf-8

from odoo import models, fields

class CustomerMemberCard(models.Model):
    _inherit = "res.company"
    member_card_logo = fields.Char(string="Member Card Logo")
