from odoo import models, fields, api

class exchange_proposale(models.Model):
    _name = 'beesdoo_bourse_shift.exchange_proposale'


    asked_timeslot_ids = fields.One2many(
        comodel_name='beesdoo_bourse_shift.exchange_proposale',
        inverse_name='id',
        string='asked_timeslots'
    )
    exchanged_timeslot_id = fields.Many2one('beesdoo_bourse_shift.timeslots_date', string='exchanged_timeslot')
    proposition_date = fields.Date(required = True)
    exchange_set_id = fields.Many2one('beesdoo_bourse_shift.exchange_set',string = 'exchanged_set')
    validate_proposale_id = fields.One2many(
        comodel_name='beesdoo_bourse_shift.exchange_proposale',
        inverse_name='id',
        string='validate_proposale'
    )
    status = fields.Char(compute='compute_status')
