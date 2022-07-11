from datetime import datetime, timedelta

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
            ("cancelled", "Cancelled"),
        ]

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="Worker",
    )

    status = fields.Selection(selection=_get_status, default="no_match")

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Exchanged shift"
    )

    exchanged_template_date = fields.Datetime(
        related="exchanged_tmpl_dated_id.date",
        readonly=True,
    )

    asked_tmpl_dated_ids = fields.Many2many(
        comodel_name="beesdoo.shift.template.dated",
        relation="exchange_template_dated",
        string="Asked shifts",
    )

    exchange_id = fields.Many2one("beesdoo.shift.exchange", string="Exchange")

    validate_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="Linked matching request"
    )

    validate_date = fields.Datetime(
        related="exchange_id.create_date",
        string="Validated on",
        readonly=True,
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
        This function checks if there aren't any other request that matches with
        the request that the cooperator made. It checks the dated template that he/she
        exchanged and the dated templates that he/she wants.

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
                    and exchange.status not in ["done", "cancelled"]
                ):
                    for asked_tmpl_dated in exchange.asked_tmpl_dated_ids:
                        if (
                            tmpl_dated_exchanged.template_id
                            == asked_tmpl_dated.template_id
                            and tmpl_dated_exchanged.date == asked_tmpl_dated.date
                        ):
                            matches |= exchange
        return matches

    @api.model
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
        """
        Send a mail to all workers that are subscribed to a shift matching
        one of asked_tmpl_dated_ids to offer them the exchange
        """
        self.ensure_one()
        for asked_tmpl in self.asked_tmpl_dated_ids:
            for worker in asked_tmpl.template_id.worker_ids:
                self.worker_id.send_mail_for_exchange(
                    self.exchanged_tmpl_dated_id, asked_tmpl, worker
                )
        return True

    @api.multi
    def send_mail_matching_request(self, matching_request):
        """
        Send a mail in case of a match between 2 exchange requests
        """
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_contact_match_coop", False
        )
        email_values = {"matching_request": matching_request}
        template_rec.with_context(email_values).send_mail(self.id, False)

    def cancel_exchange_request(self):
        self.ensure_one()
        if self.status not in ["cancelled", "done"]:
            if (
                self.validate_request_id
                and self.validate_request_id.status == "has_match"
            ):
                self.validate_request_id.status = "no_match"
                self.validate_request_id = False
            elif self.status == "has_match":
                matching_request = self.env["beesdoo.shift.exchange_request"].search(
                    [
                        ("status", "=", "awaiting_validation"),
                        ("validate_request_id", "=", self.id),
                    ],
                    limit=1,
                )
                matching_request.status = "cancelled"
                mail_template = self.env.ref(
                    "beesdoo_shift_swap.email_template_cancel_exchange_request", False
                )
                mail_template.send_mail(matching_request.id)
            self.status = "cancelled"
            return True
        return False

    @api.model
    def _warn_users_no_match(self):
        day_limit_swap = int(
            self.env["ir.config_parameter"].get_param("beesdoo_shift.day_limit_swap")
        )
        now = datetime.now()
        date_limit_up = now + timedelta(days=day_limit_swap)
        date_limit_down = now + timedelta(days=day_limit_swap - 1)
        no_matches_requests = self.search(
            [
                ("status", "=", "no_match"),
                ("exchanged_template_date", "<", date_limit_up),
                ("exchanged_template_date", ">", date_limit_down),
            ]
        )
        for request in no_matches_requests:
            email_template = self.env.ref(
                "beesdoo_shift_swap.email_template_warn_user_no_match", False
            )
            email_template.send_mail(request.id, False)

    @api.model
    def cancel_matching_requests(self, worker_id, template_id, date):
        requests = self.search(
            [
                ("worker_id", "=", worker_id.id),
                ("status", "not in", ["done", "cancelled"]),
                ("exchanged_template_date", "=", date),
            ]
        )
        for request in requests:
            if request.exchanged_tmpl_dated_id.template_id == template_id:
                request.cancel_exchange_request()
