# -*- coding: utf-8 -*-
from openerp import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    super = fields.Boolean("Super Cooperative")
    working_mode = fields.Selection(
        [
            ('regular', 'Regular worker'),
            ('irregular', 'Irregular worker'),
            ('exempt', 'Exempted'),
        ],
        string="Working mode",
    )
    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    super = fields.Boolean(related='user_ids.super', string="Super Cooperative", readonly=True)
    working_mode = fields.Selection(
        related='user_ids.working_mode',
        string="Working mode",
        readonly=True,
    )
