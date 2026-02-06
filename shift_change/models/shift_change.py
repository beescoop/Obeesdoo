from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShiftChange(models.Model):
    _name = "shift.change"
    _description = "A model to track a change of a shift"

    worker_id = fields.Many2one(
        "res.partner",
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
        domain=[("worker_id", "=", False)],
        required=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        to the old shift and subscribe him/her to the new one
        """
        res = super().create(vals_list)
        res._unsubscribe_old_shift()
        res._subscribe_new_shift()
        return res

    def _unsubscribe_old_shift(self):
        """
        Unsubscribe self.worker_id from old_shift
        Return True is unsubscription is successful.
        :return: Boolean
        """
        if (
            self.old_shift_id.worker_id
            and self.old_shift_id.worker_id == self.worker_id
        ):
            self.old_shift_id.worker_id = False
        else:
            raise ValidationError(_("You can't change shift that your are not worker."))

    def _subscribe_new_shift(self):
        """
        Subscribe self.worker_id to the new shift
        Return True is subscription is successful.
        :return: Boolean
        """
        try:
            hour_limit_change = int(
                self.env["ir.config_parameter"].get_param(
                    "shift_change.hour_limit_change"
                )
            )
        except ValueError:
            # Fall back to a default value
            hour_limit_change = 0
        if self.new_shift_id.worker_id:
            raise ValidationError(
                _("You can't subscribe to a shift assigned to someone else.")
            )
        elif self.new_shift_id.start_time <= datetime.now():
            raise ValidationError(_("You can't subscribe to a shift in the past."))
        elif self.new_shift_id.start_time <= datetime.now() + timedelta(
            hours=hour_limit_change
        ):
            raise ValidationError(
                _("You can't subscribe to a shift so close in the futur.")
            )
        else:
            self.new_shift_id.worker_id = self.worker_id
