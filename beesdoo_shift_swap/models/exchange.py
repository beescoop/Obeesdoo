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

    def is_shift_generated(self, request):
        shift = self.env["beesdoo.shift.shift"].search(
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
        return shift

    def subscribe_exchange_to_shift(self, request):
        shift = self.is_shift_generated(request)
        updated_data = {
            "worker_id": request.worker_id.id,
        }
        shift.update(updated_data)

    @api.model
    def create(self, vals):
        """
        Overriding create function to send mail to cooperator et supercooperator
        when an exchange is set.
        """
        subscr_exchange = super(Exchange, self).create(vals)
        template_rec = self.env.ref(
            "beesdoo_shift_swap.email_template_exchange_validation", False
        )
        template_rec.send_mail(subscr_exchange.first_request_id.id, False)
        template_rec.send_mail(subscr_exchange.second_request_id.id, False)
        return subscr_exchange
