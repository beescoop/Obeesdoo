from datetime import datetime, timedelta

from odoo import api, fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _description = "beesdoo.shift.solidarity.offer"

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="Worker",
    )

    state = fields.Selection(
        [
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ],
        default="validated",
    )

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    shift_id = fields.Many2one("beesdoo.shift.shift")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def subscribe_shift_if_generated(self):
        """
        Search an empty shift matching the data of the offer. If found,
        overwrite it with the worker id and the offer id.
        :return: Boolean
        """
        if self.tmpl_dated_id:
            future_subscribed_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if future_subscribed_shift:
                future_subscribed_shift.write(
                    {
                        "is_regular": True,
                        "worker_id": self.worker_id.id,
                        "solidarity_offer_ids": [(6, 0, self.ids)],
                    }
                )
                return True
        return False

    def unsubscribe_shift_if_generated(self):
        """
        Search a shift matching the data of the offer. If found,
        remove the worker and the offer from it.
        :return: Boolean
        """
        if self.tmpl_dated_id and self.state == "validated":
            subscribed_solidarity_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", self.worker_id.id),
                ],
                limit=1,
            )
            if subscribed_solidarity_shift:
                subscribed_solidarity_shift.write(
                    {
                        "is_regular": False,
                        "worker_id": False,
                        "solidarity_offer_ids": [(5,)],
                    }
                )
                subscribed_solidarity_shift.solidarity_offer_ids = None
                return True
        return False

    def check_offer_date_too_close(self):
        """
        Checks if the time delta between the current date and the shift date
        is under a limit, defined in parameter 'hours_limit_cancel_solidarity_offer'.
        :return: Boolean
        """
        now = datetime.now()
        shift_date = self.tmpl_dated_id.date
        delta = shift_date - now
        limit_hours = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.hours_limit_cancel_solidarity_offer")
        )
        if delta <= timedelta(hours=limit_hours):
            return True
        return False

    def cancel_solidarity_offer(self):
        if self.state == "validated":
            self.unsubscribe_shift_if_generated()
            self.state = "cancelled"
            return True
        return False

    @api.multi
    def counter(self):
        """
        Count the number of solidarity shifts that have been attended.
        Used in method solidarity_counter() in res.company.
        :return: Integer
        """
        counter = 0
        for record in self:
            if record.shift_id and record.shift_id.state == "done":
                counter += 1
        return counter
