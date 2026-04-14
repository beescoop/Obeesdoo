# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    def _get_counter_date_state_change(self, new_state):
        data, status = super()._get_counter_date_state_change(new_state)

        if (
            self.worker_id.working_mode == "irregular"
            and new_state in ["done", "absent_0"]
            and self.is_solidarity
        ):
            # Set status to None to prevent counter update on solidarity shift
            status = None

        return data, status
