# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SolidarityShiftOffer(models.Model):
    _name = "shift.solidarity.offer"
    _description = "Solidarity Shift Offer"

    worker_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="Worker",
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
        comodel_name="shift.shift",
        string="Generated shift",
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
    def _get_solidarity_offer_hour_limit(self):
        """Return value for solidarity_offer_hour_limit parameter"""
        try:
            solidarity_offer_hour_limit = int(
                self.env["ir.config_parameter"].get_param(
                    "shift_solidarity.solidarity_offer_hour_limit"
                )
            )
        except ValueError:
            # fall back to a default value
            solidarity_offer_hour_limit = 0
        return solidarity_offer_hour_limit

    @api.model
    def _get_shift_domain(self):
        solidarity_offer_hour_limit = self._get_solidarity_offer_hour_limit()
        return [
            (
                "start_time",
                ">=",
                datetime.now() + timedelta(hours=solidarity_offer_hour_limit),
            ),
            ("state", "=", "open"),
        ]

    @api.model
    def _get_available_shift_ids(self, worker_id):
        """List shifts available for the given worker"""
        aggregated_shifts = self.env["shift.shift"]._aggregate_sibling_shifts(
            self._get_shift_domain(),
        )
        available_shifts = self.env["shift.shift"]
        for _keys, shifts in aggregated_shifts:
            is_subscribed = bool(
                shifts.filtered(lambda rec: rec.worker_id == worker_id)
            )
            if not is_subscribed:
                for shift in shifts:
                    if not shift.worker_id:
                        # Add first empty shift and exit
                        available_shifts |= shift
                        break
        return available_shifts

    @api.model
    def _check_worker(self, worker_id):
        """Check if a worker can offer a solidarity shift"""
        # Check if user can offer solidarity shifts
        status = worker_id.cooperative_status_ids
        if (status.sr + status.sc) < 0:
            raise UserError(
                _("You can not offer a solidarity shift if your counter is below zero.")
            )

    @api.model
    def _check_shift(self, shift_id, worker_id):
        """Check if shift_id is ok to subscribe to"""
        if shift_id not in self._get_available_shift_ids(worker_id):
            raise ValidationError(
                _("You can't subscribe to this shift, it’s not available for you.")
            )

    @api.model
    def _check_unsubscribe_shift(self, shift_id, worker_id):
        """Check if worker can be unsubscribed from shift_id"""
        if shift_id.worker_id != worker_id:
            raise ValidationError(
                _(
                    "You can't subscribe to this shift, because your are not "
                    "assigned to it."
                )
            )
        if shift_id.state != "open":
            raise ValidationError(
                _("You can not subscribe to a shift in state %s." % shift_id.state)
            )
        solidarity_offer_hour_limit = self._get_solidarity_offer_hour_limit()
        if shift_id.start_time < datetime.now() + timedelta(
            hours=solidarity_offer_hour_limit
        ):
            raise ValidationError(
                _(
                    "You can not cancel this solidarity offer, because the "
                    "shift is too close in time."
                )
            )

    def _subscribe_to_shift(self):
        """Subscribe to shift_id and raise error if not possible."""
        for rec in self:
            self._check_shift(rec.shift_id, rec.worker_id)
            rec.shift_id.write(
                {
                    "worker_id": rec.worker_id.id,
                    "is_regular": True,
                    "is_compensation": False,
                }
            )

    def _unsubscribe_from_shift(self):
        """Unsubscribe of shift_id and raise error if not possible."""
        for rec in self:
            self._check_unsubscribe_shift(rec.shift_id, rec.worker_id)
            rec.shift_id.write(
                {
                    "worker_id": False,
                    "is_regular": False,
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
        self._check_worker(res.worker_id)
        if vals.get("state") == "validated":
            res._subscribe_to_shift()
        return res

    def write(self, vals):
        old_states = {}
        target_state = vals.get("state")
        for rec in self:
            old_states[rec.id] = rec.state
            self._check_worker(rec.worker_id)
        res = super().write(vals)
        for rec in self:
            old_state = old_states[rec.id]
            rec._state_change(old_state, target_state)
        return res

    def _state_change(self, old_state, new_state):
        self.ensure_one()
        if new_state == "cancelled" and old_state == "validated":
            self._unsubscribe_from_shift()
        if new_state == "validated" and old_state == "draft":
            self._subscribe_to_shift()

    def cancel_solidarity_offer(self):
        self.ensure_one()
        self.state = "cancelled"

    def count_attended_solidarity_offers(self):
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
