# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ShiftChange(models.Model):
    _inherit = "shift.change"

    @api.model
    def _check_old_shift(self, old_shift_id, worker_id):
        res = super()._check_old_shift(old_shift_id, worker_id)
        if old_shift_id.is_solidarity:
            raise ValidationError(_("You can't change a solidarity shift."))
        return res
