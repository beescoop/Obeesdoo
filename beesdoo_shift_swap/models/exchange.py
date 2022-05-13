from odoo import api, fields, models


class Exchange(models.Model):
    _name = "beesdoo.shift.exchange"
    _description = "A module to track a shift exchange between two cooperators"

    first_shift = fields.Many2one("beesdoo.shift.shift", string="First shift")
    second_shift = fields.Many2one("beesdoo.shift.shift", string="Second shift")
    first_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="First request"
    )
    second_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="Second request"
    )
    first_shift_status = fields.Boolean(default=False, string="First shift status")
    second_shift_status = fields.Boolean(default=False, string="Second shift status")

    def is_exchanged_shift_generated(self, request):
        return self.env["beesdoo.shift.shift"].search(
            [
                ("start_time", "=", request.exchanged_tmpl_dated_id.date),
                (
                    "task_template_id",
                    "=",
                    request.exchanged_tmpl_dated_id.template_id.id,
                ),
                ("worker_id", "=", request.worker_id.id),
            ],
        )

    def exchange_shifts(self):
        if not self.first_shift_status:
            first_shift = self.is_exchanged_shift_generated(self.first_request_id)
            if first_shift:
                first_shift.update(
                    {
                        "worker_id": self.second_request_id.worker_id.id,
                    }
                )
        if not self.second_shift_status:
            second_shift = self.is_exchanged_shift_generated(self.second_request_id)
            if second_shift:
                second_shift.update({"worker_id": self.first_request_id.worker_id.id})

    @api.model
    def create(self, vals):
        """
        Overriding create function to exchange workers in shifts and send mail
        to cooperator et supercooperator when an exchange is set.
        """
        exchange = super(Exchange, self).create(vals)
        exchange.exchange_shifts()
        exchange.first_request_id.write(
            {
                "validate_request_id": exchange.second_request_id.id,
                "exchange_id": exchange.id,
                "status": "done",
            }
        )
        exchange.second_request_id.write(
            {
                "exchange_id": exchange.id,
                "status": "done",
            }
        )
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_exchange_validation", False
        )
        template_rec.send_mail(exchange.first_request_id.id, False)
        template_rec.send_mail(exchange.second_request_id.id, False)
        return exchange
