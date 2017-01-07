# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    super = fields.Boolean("Super Cooperative")