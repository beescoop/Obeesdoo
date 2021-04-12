from odoo import models, fields, api

class exchange_set(models.Model):
    _name = 'beesdoo.shift.exchange_set'

    first_shift = fields.Many2one('beesdoo.shift.shift', string='first_shift')
    second_shift = fields.Many2one('beesdoo.shift.shift', string='second_shift')
    first_proposale_id=fields.One2many(
        comodel_name='beesdoo.shift.exchange_proposale',
        inverse_name='exchange_set_id',
        string='first_proposale'
    )
    second_proposale_id= fields.One2many(
        comodel_name='beesdoo.shift.exchange_proposale',
        inverse_name='exchange_set_id',
        string='second_proposale'
    )
    status_generated=fields.Selection([('exchanged_generated','0'), ('first_shift_not_generated','1'), ('second_shift_not_generated','2'), ('both_not_generated','3')])

