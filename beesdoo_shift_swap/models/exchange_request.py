from datetime import datetime

from odoo import _, api, fields, models


class ExchangeRequest(models.Model):
    _name = "beesdoo.shift.exchange_request"
    _description = "A model to track a shift exchange request"

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
    )

    asked_tmpl_dated_ids = fields.Many2many(
        comodel_name="beesdoo.shift.template.dated",
        relation="exchange_template_dated",
        string="asked_tmpl_dated",
    )
    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="exchanged_tmpl_dated"
    )

    request_date = fields.Date(
        required=True, string="Date", default=datetime.date(datetime.now())
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

    def _get_status(self):
        return [
            ("draft", "Draft"),
            ("no_match", "No Match"),
            ("has_match", "Has Match"),
            ("validate_match", "validate Match"),
            ("done", "Done"),
        ]

    status = fields.Selection(selection=_get_status, default="draft")

    @api.multi
    def name_get(self):
        data = []
        for request in self:
            display_name = "Echange : %s, %s, Proposition : " % (
                str(request.exchanged_tmpl_dated_id.template_id.name),
                fields.Date.to_string(request.exchanged_tmpl_dated_id.date),
            )
            for asked_tmpl_dated in request.asked_tmpl_dated_ids:
                display_name += "%s, %s & " % (
                    str(asked_tmpl_dated.template_id.name),
                    fields.Date.to_string(asked_tmpl_dated.date),
                )
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
                    and not exchange.status == "done"
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
        :return: beesdoo.shift.exchange_request
        """
        matches = self.env["beesdoo.shift.exchange_request"]
        exchanges = self.search([])

        for exchange in exchanges:
            if exchange.status != "done":
                for asked_tmpl_dated in exchange.asked_tmpl_dated_ids:
                    if (
                        my_tmpl_dated.template_id == asked_tmpl_dated.template_id
                        and my_tmpl_dated.date == asked_tmpl_dated.date
                    ):
                        matches |= exchange
        return matches

    def get_coop_same_days_same_hour(self, my_tmpl_dated):
        templates = self.env["beesdoo.shift.template"].search(
            [
                ("day_nb_id", "=", my_tmpl_dated.template_id.day_nb_id),
                ("start_time", "=", my_tmpl_dated.template_id.start_time),
                ("planning_id", "!=", my_tmpl_dated.template_id.planning_id.id),
            ],
        )
        worker_rec = self.env["res.partner"]
        for template in templates:
            for worker_id in template.worker_ids:
                worker_rec |= worker_id
        return worker_rec

    @api.multi
    def send_mail_matching_request(self, matching_request):
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_match_coop", False
        )
        email_values = {"matching_request": matching_request}
        template_rec.with_context(email_values).send_mail(self.id, False)
