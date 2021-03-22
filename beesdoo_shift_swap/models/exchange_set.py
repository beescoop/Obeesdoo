from odoo import models, fields, api

class exchange_set(models.Model):
    _name = 'beesdoo_bourse_shift.exchange_set'

    first_shift = fields.Many2one('beesdoo.shift.shift', string='first_shift')
    second_shift = fields.Many2one('beesdoo.shift.shift', string='second_shift')
    first_proposale_id=fields.One2many(
        comodel_name='beesdoo_bourse_shift.exchange_proposale',
        inverse_name='exchanged_set_id',
        string='first_proposale'
    )
    second_proposale_id= fields.One2many(
        comodel_name='beesdoo_bourse_shift.exchange_proposale',
        inverse_name='exchanged_set_id',
        string='second_proposale'
    )
    status_generated=fields.Selection(['exchanged_generated', 'first_shift_not_generated', 'second_shift_not_generated', 'both_not_generated'])

