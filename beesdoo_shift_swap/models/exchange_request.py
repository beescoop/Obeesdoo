from odoo import models, fields, api

class ExchangeRequest(models.Model):
    _name = 'beesdoo.shift.exchange_proposale'

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker"
    )
    #TODO : relational fields
    asked_timeslot_ids = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='asked_timeslots'
    )
    exchanged_timeslot_id = fields.Many2one('beesdoo.shift.timeslots_date', string='exchanged_timeslot')
    proposition_date = fields.Date(required = True, string='date')
    exchange_set_id = fields.Many2one('beesdoo.shift.exchange_set',string = 'exchanged_set')
    validate_proposale_id = fields.One2many(
        comodel_name='beesdoo.shift.exchange_proposale',
        inverse_name='id',
        string='validate_proposale'
    )
    def _get_status(self):
        return [
            ('draft', 'Draft'),
            ('validate', 'Validate'),
            ('done', 'Done')
        ]
    status = fields.Selection(
        selection=_get_status,
        default='draft'
    )

    def matching_request(self):
        timeslot_wanted = self.asked_timeslot_ids
        matches = self.env["beesdoo.shift.exchange.proposal"]  # Creates an empty recordset for proposals

        for rec in timeslot_wanted :
            match_exchange_rec = self.env["beesdoo.shift.exchange_proposale"]\
                .search([
                ("exchanged_timeslot_id",'=', rec.id),
            ])
            matches |= match_exchange_rec
        return matches




