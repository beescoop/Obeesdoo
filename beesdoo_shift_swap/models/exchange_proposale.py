from odoo import models, fields, api

class exchange_proposale(models.Model):
    _name = 'beesdoo.shift.exchange_proposale'

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )
    asked_timeslot_ids = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='asked_timeslots'
    )
    exchanged_timeslot_id = fields.Many2one('beesdoo.shift.timeslots_date', string='exchanged_timeslot')
    proposition_date = fields.Date(required = True)
    exchange_set_id = fields.Many2one('beesdoo.shift.exchange_set',string = 'exchanged_set')
    validate_proposale_id = fields.One2many(
        comodel_name='beesdoo.shift.exchange_proposale',
        inverse_name='id',
        string='validate_proposale'
    )
    status = fields.Char(compute='compute_status')


    def is_match(self):
        worker = self.worker_id
        my_timeslot = self.exchanged_timeslot_id
        timeslot_wanted = self.asked_timeslot_ids
        my_match = []

        for rec in timeslot_wanted :
            match_exchange_rec = self.env["beesdoo.shift.exchange_proposale"]\
                .search([
                ("exchanged_timeslot_ids",'=', rec.id),
            ])
            my_match.append(match_exchange_rec)
        if len(my_match)>0 :
            return True
        return False



