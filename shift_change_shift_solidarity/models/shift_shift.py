# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    @api.depends("is_solidarity")
    def _compute_can_be_changed(self):
        super()._compute_can_be_changed()

    def _can_be_changed(self):
        res = super()._can_be_changed()
        return not self.is_solidarity and res

    def _search_can_be_changed(self, operator, value):
        res = super()._search_can_be_changed(operator, value)
        return res + [("is_solidarity", operator, not value)]
