from odoo import models, fields, api,_
from odoo.exceptions import Warning

class ExchangeRequest(models.Model):
    _name = 'beesdoo.shift.exchange_request'
    _description = 'A model to track a shift exchange request'

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker"
    )

    asked_timeslot_ids = fields.Many2many(
        comodel_name='beesdoo.shift.template.dated',
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

    cancelled_request = fields.Many2many(
        comodel_name='beesdoo.shift.exchange_request',
        relation='cancelled_request',
        column1='beesdoo_shift_request_id1',
        column2='beesdoo_shift_request_id2',
        string='Cancelled request'
    )

    def _get_status(self):
        return [
            ('draft', 'Draft'),
            ('no_match','No Match'),
            ('has_match', 'Has Match'),
            ('validate_match', 'validate Match'),
            ('done', 'Done')
        ]
    status = fields.Selection(
        selection=_get_status,
        default='draft'
    )

    @api.multi
    def name_get(self):
        data = []
        for request in self:
            display_name = 'Echange : '
            display_name += str(request.exchanged_timeslot_id.template_id.name)
            display_name += ', '
            display_name += fields.Date.to_string(request.exchanged_timeslot_id.date)
            display_name += ', Proposition : '
            for asked_timeslot in request.asked_timeslot_ids :
                display_name += str(asked_timeslot.template_id.name)
                display_name += ', '
                display_name += fields.Date.to_string(asked_timeslot.date)
                display_name += ' & '
            data.append((request.id, display_name))
        return data

    def coop_validate_exchange(self):
        return {
            "name": _("Validate Exchange"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.validate.shift.exchange",
            "target": "new",
        }

    def matching_request(self, timeslots_wanted, timeslot_exchanged):
        """
        This function check if there aren't any other request that match with
        the request that the cooperator made. It check the timeslot that he
        exchanged and timeslots that he wanted.

        :param timeslots_wanted: beesdoo.shift.template.dated recordset
        :param timeslot_exchanged: beesdoo.shift.template.dated  record
        :return: beesdoo.shift.exchange_request recordset
        """
        matches = self.env["beesdoo.shift.exchange_request"]  # Creates an empty recordset for proposals
        exchanges = self.env["beesdoo.shift.exchange_request"].search([])

        for timeslot in timeslots_wanted :
            for exchange in exchanges :
                if timeslot.template_id == exchange.exchanged_timeslot_id.template_id and timeslot.date==exchange.exchanged_timeslot_id.date and not exchange.status == "done":
                    for asked_timeslot in exchange.asked_timeslot_ids :
                        if timeslot_exchanged.template_id == asked_timeslot.template_id and timeslot_exchanged.date == asked_timeslot.date :
                            matches |= exchange
        return matches

    def get_possible_match(self,my_timeslot):
        """
        Check if there aren't any beesdoo.shift.exchange_request record that match
        with "my_timeslot".
        :param my_timeslot: beesdoo.shift.template.dated
        :return: beesdoo.shift.exchange_request
        """
        matches = self.env["beesdoo.shift.exchange_request"]  # Creates an empty recordset for proposals
        exchanges = self.env["beesdoo.shift.exchange_request"].search([])

        for exchange in exchanges :
            if exchange.status != 'done' :
                for asked_timeslot in exchange.asked_timeslot_ids:
                    if my_timeslot.template_id == asked_timeslot.template_id and my_timeslot.date == asked_timeslot.date:
                        matches |= exchange
        return matches

    def get_coop_same_days_same_hour(self,my_timeslot):
        exchange_request = self.env["beesdoo.shift.template"].search([])
        worker_rec = self.env["res.partner"]
        for rec in exchange_request :
            if my_timeslot.template_id.day_nb_id == rec.day_nb_id and my_timeslot.template_id.start_time == rec.start_time and not my_timeslot.template_id.name == rec.name:
                for record in rec.worker_ids :
                    worker_rec |= record
        return worker_rec

    @api.multi
    def send_mail_matching_request(self, matching_request):
        template_rec = self.env.ref("beesdoo_shift_swap.email_template_contact_match_coop", False)
        email_values = {
            "matching_request": matching_request
        }
        template_rec.with_context(email_values).send_mail(self.id, False)
