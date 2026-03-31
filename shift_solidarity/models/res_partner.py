# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def worker_offer_solidarity(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "shift.solidarity.offer",
            "view_mode": "form",
            "target": "new",
            "context": {
                "solidarity_auto_validate": True,
                "default_worker_id": self.id,
            },
        }

    def worker_request_solidarity(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "shift.solidarity.request",
            "view_mode": "form",
            "target": "new",
            "context": {
                "solidarity_auto_validate": True,
                "default_worker_id": self.id,
            },
        }
