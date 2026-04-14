# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class SolidarityShiftRequest(models.Model):
    _inherit = "shift.solidarity.request"

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if vals.get("state") == "validated":
            res.worker_id.cooperative_status_ids[0].sr += 1
        return res

    def state_change(self, old_state, new_state):
        super().state_change(old_state, new_state)
        if self.worker_id.working_mode == "irregular":
            if new_state == "validated" and old_state == "draft":
                self.worker_id.cooperative_status_ids[0].sr += 1
            if new_state == "cancelled" and old_state == "validated":
                self.worker_id.cooperative_status_ids[0].sr -= 1
