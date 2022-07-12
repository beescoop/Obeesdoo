from datetime import datetime, timedelta

from odoo import api, fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _inherit = ["beesdoo.shift.swap.mixin"]
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

    shift_date = fields.Datetime(
        related="tmpl_dated_id.date",
        readonly=True,
    )

    shift_id = fields.Many2one("beesdoo.shift.shift", string="Generated shift")

    def create(self, vals_list):
        """
        Override create() method to subscribe the worker
        to the shift if it is generated
        """
        res = super(SolidarityShiftOffer, self).create(vals_list)
        res._subscribe_shift_if_generated()
        return res

    def _subscribe_shift_if_generated(self):
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

    def _unsubscribe_shift_if_generated(self):
        """
        Search a shift matching the data of the offer. If found,
        remove the worker and the offer from it.
        :return: Boolean
        """
        if (
            self.tmpl_dated_id
            and self.tmpl_dated_id.date > datetime.now()
            and self.state == "validated"
        ):
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
                        "is_solidarity": False,
                        "worker_id": False,
                        "solidarity_offer_ids": [(5,)],
                    }
                )
                return True
        return False

    def check_offer_date_too_close(self):
        """
        Checks if the time delta between the current date and the shift date
        is under a limit, defined in parameter 'min_hours_to_unsubscribe'.
        Returns True if the date is too close.
        :return: Boolean
        """
        self.ensure_one()
        shift_date = self.tmpl_dated_id.date
        delta = shift_date - datetime.now()
        limit_hours = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.min_hours_to_unsubscribe")
        )
        if delta <= timedelta(hours=limit_hours):
            return True
        return False

    def cancel_solidarity_offer(self):
        self.ensure_one()
        if self.state == "validated" and not self.check_offer_date_too_close():
            self._unsubscribe_shift_if_generated()
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

    def update_shift_data(self, shift, swap_subscription_done):
        done = False
        if (
            not shift["worker_id"]
            and shift["task_template_id"] == self.tmpl_dated_id.template_id.id
            and shift["start_time"] == self.tmpl_dated_id.date
        ):
            shift["worker_id"] = self.worker_id.id
            shift["is_regular"] = True
            shift["solidarity_offer_ids"] = [(6, 0, self.ids)]
            done = True
        return shift, swap_subscription_done, done
