# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    can_be_changed = fields.Boolean(
        compute="_compute_can_be_changed",
        search="_search_can_be_changed",
    )

    @api.depends()
    def _compute_can_be_changed(self):
        for rec in self:
            rec.can_be_changed = rec._can_be_changed()

    def _can_be_changed(self):
        """Override this method to restrict the ability of a shift to be
        changed"""
        self.ensure_one()
        return True

    def _search_can_be_changed(self, operator, value):
        """Override this method implement search domain for the
        can_be_changed field"""
        return []
