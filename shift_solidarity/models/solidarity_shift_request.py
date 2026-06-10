# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SolidarityShiftRequest(models.Model):
    _name = "shift.solidarity.request"
    _description = "Solidarity Shift Request"

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
        states={"validated": [("readonly", True)], "cancelled": [("readonly", True)]},
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        states={"cancelled": [("readonly", True)]},
    )

    shift_id = fields.Many2one(
        "shift.shift",
        string="Shift",
        states={"validated": [("readonly", True)], "cancelled": [("readonly", True)]},
    )

    reason = fields.Text(
        default="",
        states={"validated": [("readonly", True)], "cancelled": [("readonly", True)]},
    )

    def name_get(self):
        res = []
        for rec in self:
            name = "{} - {}".format(
                rec.worker_id.name,
                rec.shift_id.name,
            )
            res.append((rec.id, name))
        return res

    @api.model
    def _get_solidarity_request_hour_limit(self):
        """Return value for solidarity_request_hour_limit parameter"""
        try:
            solidarity_request_hour_limit = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("shift_solidarity.solidarity_request_hour_limit")
            )
        except ValueError:
            # fall back to a default value
            solidarity_request_hour_limit = 0
        return solidarity_request_hour_limit

    @api.model
    def _check_max_solidarity_requests_number(self, worker_id):
        """
        Check if the worker has reached the limit of solidarity requests,
        defined in parameter 'max_solidarity_requests_number'.
        Raise error if so.
        """
        # Count the requests created in the last 365 days
        nb_requests = self.search_count(
            [
                ("worker_id", "=", worker_id.id),
                ("state", "=", "validated"),
                ("create_date", ">", datetime.now() - timedelta(days=365)),
            ],
        )
        try:
            max_solidarity_requests = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("shift_solidarity.max_solidarity_requests_number")
            )
        except ValueError:
            # fall back to a default value
            max_solidarity_requests = -1

        if max_solidarity_requests >= 0 and nb_requests > max_solidarity_requests:
            raise ValidationError(_("Too many solidarity request for this partner."))

    @api.model
    def _check_shift(self, shift_id, worker_id):
        """Check that it is ok to unsubscribe from a shift."""
        if shift_id.worker_id != worker_id:
            raise UserError(
                _(
                    "You can not request solidarity for a shift your are not "
                    "assigned to."
                )
            )
        if shift_id.state != "open":
            raise UserError(
                _("You can not request solidarity for a shift %s." % shift_id.state)
            )
        solidarity_request_hour_limit = self._get_solidarity_request_hour_limit()
        if shift_id.start_time < (
            datetime.now() + timedelta(hours=solidarity_request_hour_limit)
        ):
            raise UserError(
                _("You can not request solidarity for a shift soo close in the time.")
            )

    @api.model
    def _check_subscribe_shift(self, shift_id, worker_id):
        if shift_id.worker_id:
            raise UserError(_("You can’t subscribe to a non empty shift."))
        if shift_id.state != "open":
            raise UserError(
                _("You can not subscribe to a shift in state %s." % shift_id.state)
            )
        if shift_id.start_time < datetime.now():
            raise UserError(_("You can not subscribe to a shift in the past."))

    @api.model
    def _get_shift_domain(self, worker_id):
        solidarity_request_hour_limit = self._get_solidarity_request_hour_limit()
        shift_domain = [
            ("worker_id", "=", worker_id.id),
            (
                "start_time",
                ">=",
                datetime.now() + timedelta(hours=solidarity_request_hour_limit),
            ),
        ]
        return shift_domain

    @api.onchange("worker_id")
    def _on_change_worker_id(self):
        return {"domain": {"shift_id": self._get_shift_domain(self.worker_id)}}

    def _unsubscribe_from_shift(self):
        """Unsubscribe worker from shift"""
        for request in self:
            self._check_shift(request.shift_id, request.worker_id)
            request.shift_id.write(
                {
                    "worker_id": False,
                    "is_regular": False,
                    "is_compensation": False,
                }
            )

    def _subscribe_to_shift(self):
        """Subscribe the worker to the shift"""
        for request in self:
            self._check_subscribe_shift(request.shift_id, request.worker_id)
            request.shift_id.write(
                {
                    "worker_id": request.worker_id.id,
                    "is_regular": True,
                    "is_compensation": False,
                }
            )

    @api.model
    def create(self, vals):
        if vals.get("state") == "draft" and self.env.context.get(
            "solidarity_auto_validate"
        ):
            vals["state"] = "validated"
        res = super().create(vals)
        self.env["res.company"]._check_counter_limit()
        self._check_max_solidarity_requests_number(res.worker_id)
        if vals.get("state") == "validated":
            res._unsubscribe_from_shift()
        return res

    def write(self, vals):
        old_states = {}
        target_state = vals.get("state")
        for rec in self:
            old_states[rec.id] = rec.state
        res = super().write(vals)
        self.env["res.company"]._check_counter_limit()
        for rec in self:
            self._check_max_solidarity_requests_number(rec.worker_id)
            old_state = old_states[rec.id]
            rec.state_change(old_state, target_state)
        return res

    def state_change(self, old_state, new_state):
        self.ensure_one()
        if new_state == "cancelled" and old_state == "validated":
            self._subscribe_to_shift()
        if new_state == "validated" and old_state == "draft":
            self._unsubscribe_from_shift()

    def cancel_solidarity_request(self):
        self.ensure_one()
        self.state = "cancelled"
