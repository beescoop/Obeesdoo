# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    super = fields.Boolean("Super Cooperative")
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    super = fields.Boolean(related='user_ids.super', string="Super Cooperative", readonly=True)