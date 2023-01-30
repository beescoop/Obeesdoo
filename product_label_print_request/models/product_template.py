# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    label_to_be_printed = fields.Boolean("Print label?")
    label_last_printed = fields.Datetime("Label last printed on")

    @api.multi
    def create_request_label_printing_wizard(self):
        context = {"active_ids": self.ids}
        self.env["label.printing.wizard"].with_context(context).create({})
        print_request_view = self.env.ref(
            "product_label_print_request.printing_label_request_wizard"
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "label.printing.wizard",
            "view_type": "form",
            "view_mode": "form",
            "print_request_view": print_request_view.id,
            "target": "new",
        }
