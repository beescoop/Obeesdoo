import math
from datetime import datetime, timedelta

from odoo import api, fields, models


def float_to_time(f):
    decimal, integer = math.modf(f)
    return "{}:{}".format(
        str(int(integer)).zfill(2), str(int(round(decimal * 60))).zfill(2)
    )


class SolidarityShiftRequest(models.Model):
    _name = "beesdoo.shift.solidarity.request"
    _inherit = ["beesdoo.shift.swap.mixin"]
    _description = "beesdoo.shift.solidarity.request"

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
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

    reason = fields.Text(string="Reason", default="")

    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        from the shift and update the counters
        """
        res = super(SolidarityShiftRequest, self).create(vals_list)
        if res.worker_id.working_mode == "regular":
            res._unsubscribe_shift_if_generated()
        res.update_personal_counter()
        self.env["beesdoo.shift.exchange_request"].cancel_matching_requests(
            res.worker_id, res.tmpl_dated_id.template_id, res.tmpl_dated_id.date
        )
        return res

    def _unsubscribe_shift_if_generated(self):
        """
        Search a shift matching the data of the request. If found,
        remove the worker from it.
        :return: Boolean
        """
        if self.tmpl_dated_id and self.tmpl_dated_id.date > datetime.now():
            non_realisable_shift = self.env["shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", self.tmpl_dated_id.template_id.id),
                    ("worker_id", "=", self.worker_id.id),
                ],
                limit=1,
            )
            if non_realisable_shift:
                non_realisable_shift.write({"is_regular": False, "worker_id": False})
                return True
        return False

    def _subscribe_shift_if_generated(self):
        """
        Search an empty shift matching the data of the request. If found,
        overwrite it with the worker id and the offer id. If not, create a
        new one with the data.
        :return: Boolean
        """
        if (
            self.tmpl_dated_id
            and self.tmpl_dated_id.date > datetime.now()
            and self.state == "validated"
        ):
            template_id = self.tmpl_dated_id.template_id
            unsubscribed_shift = self.env["shift.shift"].search(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", template_id.id),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if unsubscribed_shift:
                unsubscribed_shift.write(
                    {
                        "is_regular": True,
                        "worker_id": self.worker_id.id,
                    }
                )
                return True

            # If there are no empty shift corresponding
            nb_shift = self.env["shift.shift"].search_count(
                [
                    ("start_time", "=", self.tmpl_dated_id.date),
                    ("task_template_id", "=", template_id.id),
                ],
            )
            if nb_shift > 0:
                # Create a new shift
                data = {
                    "name": "[%s] %s %s (%s - %s) [%s]"
                    % (
                        self.tmpl_dated_id.date.date(),
                        template_id.planning_id.name,
                        template_id.day_nb_id.name,
                        float_to_time(template_id.start_time),
                        float_to_time(template_id.end_time),
                        nb_shift,
                    ),
                    "task_template_id": template_id.id,
                    "task_type_id": template_id.task_type_id.id,
                    "super_coop_id": template_id.super_coop_id.id,
                    "worker_id": self.worker_id and self.worker_id.id or False,
                    "is_regular": bool(self.worker_id),
                    "start_time": self.tmpl_dated_id.date,
                    "end_time": self.tmpl_dated_id.date
                    + timedelta(hours=template_id.end_time - template_id.start_time),
                    "state": "open",
                }
                self.env["shift.shift"].create(data)
                return True
        return False

    def cancel_solidarity_request(self):
        self.ensure_one()
        if self.can_cancel_request():
            self._subscribe_shift_if_generated()
            self.state = "cancelled"
            self.update_personal_counter()
            return True
        return False

    def can_cancel_request(self):
        return self.state == "validated" and (
            self.worker_id.working_mode == "irregular"
            or self.tmpl_dated_id.date > datetime.now()
            or self.tmpl_dated_id.date < self.create_date
        )

    @api.model
    def check_solidarity_requests_number(self, worker_id, requested_shift_date=False):
        """
        Check if the worker has reached the limit of solidarity requests,
        defined in parameter 'max_solidarity_requests_number'.
        Return True if the limit is not reached.
        :param worker_id: res.partner id
        :param requested_shift_date: datetime (should be provided if worker is regular)
        :return: Boolean
        """
        if worker_id.working_mode == "regular" and requested_shift_date:
            # Count the requests in the 365 days before the date of the shift
            nb_requests = self.sudo().search_count(
                [
                    ("worker_id", "=", worker_id.id),
                    ("state", "=", "validated"),
                    (
                        "tmpl_dated_id.date",
                        ">",
                        requested_shift_date - timedelta(days=365),
                    ),
                ],
            )
        else:
            # Count the requests created in the last 365 days
            nb_requests = self.sudo().search_count(
                [
                    ("worker_id", "=", worker_id.id),
                    ("state", "=", "validated"),
                    ("create_date", ">", datetime.now() - timedelta(days=365)),
                ],
            )

        return nb_requests < int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.max_solidarity_requests_number")
        )

    def update_personal_counter(self):
        """
        Override this method to define the counters behaviour when
        creating and cancelling a solidarity request
        """
        return True

    @api.model
    def counter(self):
        """
        Count the number of solidarity requests that have been validated in self.
        Used in method solidarity_counter() in res.company.
        :return: Integer
        """
        return self.search_count([("state", "=", "validated")])

    def update_shift_data(self, shift, swap_subscription_done):
        """
        See method info in model beesdoo.shift.swap.mixin
        """
        self.ensure_one()
        done = False
        if (
            shift["worker_id"] == self.worker_id.id
            and self.tmpl_dated_id
            and shift["task_template_id"] == self.tmpl_dated_id.template_id.id
            and shift["start_time"] == self.tmpl_dated_id.date
        ):
            shift["worker_id"] = False
            shift["is_regular"] = False
            done = True
        return shift, swap_subscription_done, done
