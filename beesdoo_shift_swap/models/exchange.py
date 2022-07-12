from odoo import api, fields, models


class Exchange(models.Model):
    _name = "beesdoo.shift.exchange"
    _inherit = ["beesdoo.shift.swap.mixin"]
    _description = "A module to track a shift exchange between two cooperators"

    first_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="First exchange request"
    )

    second_request_id = fields.Many2one(
        "beesdoo.shift.exchange_request", string="Second exchange request"
    )

    def search_shift_generated(self, request):
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
            limit=1,
        )

    @api.multi
    def update_shifts_if_generated(self):
        """
        Exchange the worker_id of the 2 shifts if they are generated
        """
        for rec in self:
            if rec.first_request_id:
                first_shift = rec.search_shift_generated(rec.first_request_id)
                if first_shift:
                    first_shift.update(
                        {
                            "worker_id": rec.second_request_id.worker_id.id,
                        }
                    )
            if rec.second_request_id:
                second_shift = rec.search_shift_generated(rec.second_request_id)
                if second_shift:
                    second_shift.update(
                        {"worker_id": rec.first_request_id.worker_id.id}
                    )

    @api.model
    def create(self, vals):
        """
        Overriding create function to exchange workers in shifts and send mail
        to cooperator and supercooperator when an exchange is set.
        """
        exchange = super(Exchange, self).create(vals)
        exchange.update_shifts_if_generated()
        exchange.first_request_id.write(
            {
                "validate_request_id": exchange.second_request_id.id,
                "exchange_id": exchange.id,
                "status": "done",
            }
        )
        exchange.second_request_id.write(
            {
                "validate_request_id": exchange.first_request_id.id,
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

    def update_shift_data(self, shift, swap_subscription_done):
        if (
            shift["worker_id"] == self.first_request_id.worker_id.id
            and self.first_request_id.exchanged_tmpl_dated_id.template_id.id
            == shift["task_template_id"]
            and shift["start_time"]
            == self.first_request_id.exchanged_tmpl_dated_id.date
        ):
            shift["worker_id"] = self.second_request_id.worker_id.id
            shift["is_regular"] = True
        if (
            shift["worker_id"] == self.second_request_id.worker_id.id
            and shift["task_template_id"]
            == self.second_request_id.exchanged_tmpl_dated_id.template_id.id
            and shift["start_time"]
            == self.second_request_id.exchanged_tmpl_dated_id.date
        ):
            shift["worker_id"] = self.first_request_id.worker_id.id
            shift["is_regular"] = True
        return shift, swap_subscription_done, False
