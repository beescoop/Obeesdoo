# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class ShiftShift(models.Model):

    _inherit = "shift.shift"

    solidarity_offer_ids = fields.One2many(
        comodel_name="shift.solidarity.offer",
        inverse_name="shift_id",
        string="Solidarity shift offer",
    )

    is_solidarity = fields.Boolean(
        string="Solidarity shift",
        readonly=True,
        store=True,
        compute="_compute_is_solidarity",
    )

    def subscribe_shift_as_solidarity(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "shift.solidarity.offer",
            "view_mode": "form",
            "target": "new",
            "context": {
                "solidarity_auto_validate": True,
                "default_shift_id": self.id,
            },
        }

    @api.depends("solidarity_offer_ids")
    def _compute_is_solidarity(self):
        for rec in self:
            rec.is_solidarity = any(
                state == "validated"
                for state in rec.solidarity_offer_ids.mapped("state")
            )

    def cancel_solidarity_offer(self):
        self.ensure_one()
        if self.is_solidarity:
            return self.solidarity_offer_ids[0].cancel_solidarity_offer()
        return False
