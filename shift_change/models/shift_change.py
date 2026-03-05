# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShiftChange(models.Model):
    _name = "shift.change"
    _description = "A model to track a change of a shift"
    _order = "create_date desc"

    worker_id = fields.Many2one(
        "res.partner",
        string="Worker",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        required=True,
    )
    old_shift_id = fields.Many2one("shift.shift", string="Old shift", required=True)
    new_shift_id = fields.Many2one(
        "shift.shift",
        string="New shift",
        required=True,
    )

    def name_get(self):
        res = []
        for rec in self:
            name = "{} - {} -> {}".format(
                rec.worker_id.name,
                rec.old_shift_id.start_time,
                rec.new_shift_id.start_time,
            )
            res.append((rec.id, name))
        return res

    @api.model
    def _get_hour_limit_change(self):
        """Return value for hour_limit_change parameter"""
        try:
            hour_limit_change = int(
                self.env["ir.config_parameter"].get_param(
                    "shift_change.hour_limit_change"
                )
            )
        except ValueError:
            # fall back to a default value
            hour_limit_change = 0
        return hour_limit_change

    @api.model
    def _get_available_new_shift_ids(self, worker_id):
        """List new shifts available for the given worker"""
        aggregated_shifts = self.env["shift.shift"]._aggregate_sibling_shifts(
            [
                ("start_time", ">=", datetime.now()),
                ("state", "=", "open"),
            ],
        )
        available_new_shifts = self.env["shift.shift"]
        for _keys, shifts in aggregated_shifts:
            is_subscribed = bool(
                shifts.filtered(lambda rec: rec.worker_id == worker_id)
            )
            if not is_subscribed:
                for shift in shifts:
                    if not shift.worker_id:
                        # Add first empty shift and exit
                        available_new_shifts |= shift
                        break
        return available_new_shifts

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        to the old shift and subscribe him/her to the new one
        """
        res = super().create(vals_list)
        res._subscribe_new_shift()
        res._unsubscribe_old_shift()
        return res

    def _unsubscribe_old_shift(self):
        """
        Unsubscribe self.worker_id from old_shift
        Raise error if not possible.
        """
        self._check_old_shift(self.old_shift_id, self.worker_id)
        self.old_shift_id.write(
            {
                "worker_id": False,
                "is_regular": False,
                "is_compensation": False,
            }
        )

    def _subscribe_new_shift(self):
        """
        Subscribe self.worker_id to the new shift
        Raise error if not possible.
        """
        self._check_new_shift(self.new_shift_id)
        self.new_shift_id.write(
            {
                "worker_id": self.worker_id.id,
                "is_regular": self.old_shift_id.is_regular,
                "is_compensation": self.old_shift_id.is_compensation,
            }
        )

    @api.model
    def _check_old_shift(self, old_shift_id, worker_id):
        """Check if old shift can be changed"""
        hour_limit_change = self._get_hour_limit_change()
        if not old_shift_id.worker_id or old_shift_id.worker_id != worker_id:
            raise ValidationError(_("You can't change shift that your are not worker."))
        if old_shift_id.start_time <= datetime.now():
            raise ValidationError(_("You can't change shift that is in the past."))
        if old_shift_id.start_time <= datetime.now() + timedelta(
            hours=hour_limit_change
        ):
            raise ValidationError(_("You can't change a shift so close in the futur."))
        try:
            same_shift_change_max = int(
                self.env["ir.config_parameter"].get_param(
                    "shift_change.same_shift_change_max"
                )
            )
        except ValueError:
            # fall back to a default value
            same_shift_change_max = 0
        if same_shift_change_max:
            same_shift_change_nb = 0
            tmp_old_shift_id = old_shift_id
            previous_changes = self.env["shift.change"]
            while tmp_old_shift_id and same_shift_change_nb <= same_shift_change_max:
                change = self.search(
                    [
                        ("new_shift_id", "=", tmp_old_shift_id.id),
                        ("worker_id", "=", worker_id.id),
                        ("id", "not in", previous_changes.ids),
                    ],
                    limit=1,
                )
                if change:
                    same_shift_change_nb += 1
                    tmp_old_shift_id = change.old_shift_id
                    previous_changes |= change
                else:
                    tmp_old_shift_id = None
            if same_shift_change_nb >= same_shift_change_max:
                raise ValidationError(
                    _(
                        "You can't change the same shift more than"
                        f"{same_shift_change_max} times."
                    )
                )

    @api.model
    def _check_new_shift(self, new_shift_id):
        """Check if shift can be changed or not"""
        hour_limit_change = self._get_hour_limit_change()
        if new_shift_id.worker_id:
            raise ValidationError(
                _("You can't subscribe to a shift assigned to someone else.")
            )
        if new_shift_id.start_time <= datetime.now():
            raise ValidationError(_("You can't subscribe to a shift in the past."))
        if new_shift_id.start_time <= datetime.now() + timedelta(
            hours=hour_limit_change
        ):
            raise ValidationError(
                _("You can't subscribe to a shift so close in the futur.")
            )
        if new_shift_id not in self._get_available_new_shift_ids(self.worker_id):
            raise ValidationError(
                _("You can't subscribe to this shift, it’s not available for you.")
            )
