from datetime import datetime

from odoo import _, api, fields, models


class ExchangeRequest(models.Model):
    _name = "beesdoo.shift.exchange_request"
    _description = "A model to track a shift exchange request"

    def _get_status(self):
        return [
            ("no_match", "No match"),
            ("has_match", "Has match"),
            ("awaiting_validation", "Awaiting validation"),
            ("done", "Done"),
        ]

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
    )

    status = fields.Selection(selection=_get_status, default="no_match")

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="exchanged_tmpl_dated"
    )

    asked_tmpl_dated_ids = fields.Many2many(
        comodel_name="beesdoo.shift.template.dated",
        relation="exchange_template_dated",
        string="asked_tmpl_dated",
    )

    exchange_id = fields.Many2one("beesdoo.shift.exchange", string="exchange")

    validate_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="validate_request"
    )

    cancelled_request = fields.Many2many(
        comodel_name="beesdoo.shift.exchange_request",
        relation="cancelled_request",
        column1="beesdoo_shift_request_id1",
        column2="beesdoo_shift_request_id2",
        string="Cancelled request",
    )

    @api.multi
    def name_get(self):
        data = []
        for request in self:
            display_name = "Worker : %s,\nExchanged shift : %s %s" % (
                str(request.worker_id.name),
                str(request.exchanged_tmpl_dated_id.template_id.name),
                fields.Date.to_string(request.exchanged_tmpl_dated_id.date),
            )
            data.append((request.id, display_name))
        return data

    @api.model
    def create(self, vals):
        """
        Overriding create function to update the status
        """
        request = super(ExchangeRequest, self).create(vals)
        if request.validate_request_id:
            request.status = "awaiting_validation"
            request.validate_request_id.status = "has_match"
        return request

    def coop_validate_exchange(self):
        return {
            "name": _("Validate Exchange"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.validate.shift.exchange",
            "target": "new",
        }

    def matching_request(self, tmpl_dated_wanted, tmpl_dated_exchanged):
        """
        This function check if there aren't any other request that match with
        the request that the cooperator made. It checks the dated template that he
        exchanged and the dated templates that he wanted.

        :param tmpl_dated_wanted: beesdoo.shift.template.dated recordset
        :param tmpl_dated_exchanged: beesdoo.shift.template.dated  record
        :return: beesdoo.shift.exchange_request recordset
        """
        matches = self.env["beesdoo.shift.exchange_request"]
        exchanges = self.search([])

        for tmpl_dated in tmpl_dated_wanted:
            for exchange in exchanges:
                if (
                    tmpl_dated.template_id
                    == exchange.exchanged_tmpl_dated_id.template_id
                    and tmpl_dated.date == exchange.exchanged_tmpl_dated_id.date
                    and exchange.status != "done"
                ):
                    for asked_tmpl_dated in exchange.asked_tmpl_dated_ids:
                        if (
                            tmpl_dated_exchanged.template_id
                            == asked_tmpl_dated.template_id
                            and tmpl_dated_exchanged.date == asked_tmpl_dated.date
                        ):
                            matches |= exchange
        return matches

    def get_possible_match(self, my_tmpl_dated):
        """
        Check if there aren't any beesdoo.shift.exchange_request record that match
        with "my_tmpl_dated".
        :param my_tmpl_dated: beesdoo.shift.template.dated
        :return: beesdoo.shift.exchange_request recordset
        """
        matches = self.env["beesdoo.shift.exchange_request"]
        exchange_requests = self.search(
            [
                ("status", "=", "no_match"),
                ("exchanged_tmpl_dated_id.date", ">", datetime.now()),
            ],
        )

        for request in exchange_requests:
            for asked_tmpl_dated in request.asked_tmpl_dated_ids:
                if (
                    my_tmpl_dated.template_id == asked_tmpl_dated.template_id
                    and my_tmpl_dated.date == asked_tmpl_dated.date
                ):
                    matches |= request
        return matches

    def send_mail_wanted_tmpl_dated(self):
        self.ensure_one()
        for asked_tmpl in self.asked_tmpl_dated_ids:
            for worker in asked_tmpl.template_id.worker_ids:
                self.worker_id.send_mail_for_exchange(
                    self.exchanged_tmpl_dated_id, asked_tmpl, worker
                )
        return True

    @api.multi
    def send_mail_matching_request(self, matching_request):
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_match_coop", False
        )
        email_values = {"matching_request": matching_request}
        template_rec.with_context(email_values).send_mail(self.id, False)
