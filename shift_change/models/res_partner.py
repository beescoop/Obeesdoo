# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import _, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def button_change_shift(self):
        return {
            "name": _("Change a Shift"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "shift.change.create.wizard",
            "target": "new",
        }
