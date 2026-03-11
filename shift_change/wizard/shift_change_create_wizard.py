# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime, timedelta

from odoo import api, fields, models


class ShiftChangeCreateWizard(models.TransientModel):
    _name = "shift.change.create.wizard"
    _description = "Wizard to create a shift change"

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
        required=True,
    )
    available_new_shift_ids = fields.Many2many(
        "shift.shift",
        string="Available New Shifts",
        compute="_compute_available_new_shift_ids",
    )

    @api.onchange("worker_id")
    def _on_change_worker_id(self):
        old_shift_hour_limit_change = self.env[
            "shift.change"
        ]._get_old_shift_hour_limit_change()
        old_shift_domain = [
            ("worker_id", "=", self.worker_id.id),
            (
                "start_time",
                ">=",
                datetime.now() + timedelta(hours=old_shift_hour_limit_change),
            ),
        ]
        return {
            "domain": {
                "old_shift_id": old_shift_domain,
            }
        }

    @api.depends("worker_id", "old_shift_id")
    def _compute_available_new_shift_ids(self):
        for rec in self:
            rec.available_new_shift_ids = self.env[
                "shift.change"
            ]._get_available_new_shift_ids(rec.worker_id)

    def action_confirm(self):
        self.env["shift.change"].create(
            {
                "worker_id": self.worker_id.id,
                "old_shift_id": self.old_shift_id.id,
                "new_shift_id": self.new_shift_id.id,
            }
        )
