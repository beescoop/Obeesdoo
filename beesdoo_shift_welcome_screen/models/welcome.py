# Copyright 2021 Coop IT Easy SCRL fs
#   Thibault François
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import _, api, fields, models


class TaskType(models.TransientModel):
    _name = "beesdoo.shift.welcome"

    _inherit = ["barcodes.barcode_events_mixin"]

    partner_id = fields.Many2one("res.partner", string="Cooperator")
    message = fields.Html("Message")

    def on_barcode_scanned(self, barcode):
        self._barcode_scanned = ""
        self.message = ""

        if barcode.startswith("42"):
            barcode = "0" + barcode
        if not barcode.startswith("042"):
            self.message = _("Invalid barcode")
            return
        # 0 at the begining of the code bar seems not to be scanned
        partner_ids = self.env["res.partner"].search([("barcode", "=", barcode)])
        if not partner_ids:
            self.message = _("Member does not exist")
        elif len(partner_ids) > 1:
            self.message = _("More then one member found with this barcode")
        else:
            self.partner_id = partner_ids[0]

    @api.onchange("partner_id")
    def _onchange_partner(self):
        partner = self.partner_id
        partner = partner.parent_eater_id if partner.parent_eater_id else partner
        values = {
            "rec": self,
            "partner": partner,
            "next_shift": self._get_next_shift(partner),
        }
        html_res = self.env.ref("beesdoo_shift_welcome_screen.welcome_message").render(
            values
        )
        self.message = html_res

    def _get_next_shift(self, partner):
        if not partner:
            return self.env["shift.shift"]
        now = datetime.now()
        return self.env["shift.shift"].search(
            [
                ("start_time", ">", now),
                ("worker_id", "=", partner.id),
            ],
            order="start_time, task_template_id, task_type_id",
        )
