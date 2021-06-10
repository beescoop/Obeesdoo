from odoo import models, fields, api
from odoo.exceptions import Warning

class ExchangeRequest(models.Model):
    _name = 'beesdoo.shift.exchange_request'

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
    asked_timeslot_ids = fields.Many2many(
        comodel_name='beesdoo.shift.template.dated',
        #inverse_name='id',
        relation='exchange_template_dated',
        string='asked_timeslots'
    )
    exchanged_timeslot_id = fields.Many2one('beesdoo.shift.template.dated', string='exchanged_timeslot')
    request_date = fields.Date(required = True, string='date')
    exchange_id = fields.Many2one('beesdoo.shift.exchange',string = 'exchange')
    validate_request_id = fields.Many2one(
        'beesdoo.shift.exchange_request',
        string='validate_request'
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

    '''def display_request(self):
        my_timeslot = self.exchanged_timeslot_id
        all_timeslot = self.env["beesdoo.shift.template.dated"].display_timeslot(my_timeslot)
        requests = self.env["beesdoo.shift.exchange_request"].search([])
        for request in requests :
            if'''



    def matching_request(self, timeslots_wanted, timeslot_exchanged):
        #timeslot_wanted = self.asked_timeslot_ids
        matches = self.env["beesdoo.shift.exchange_request"]  # Creates an empty recordset for proposals
        exchanges = self.env["beesdoo.shift.exchange_request"].search([])

        for timeslot in timeslots_wanted :
            for exchange in exchanges :
                if timeslot.template_id == exchange.exchanged_timeslot_id.template_id and timeslot.date==exchange.exchanged_timeslot_id.date :
                    for asked_timeslot in exchange.asked_timeslot_ids :
                        if timeslot_exchanged.template_id == asked_timeslot.template_id and timeslot_exchanged.date ==asked_timeslot.date :
                            matches |= exchange
        return matches

    @api.multi
    def button_unsubscribe(self):
        for request in self:
            if not request.matching_request(request.asked_timeslot_ids,request.exchanged_timeslot_id):
                raise Warning('no match')
        return True