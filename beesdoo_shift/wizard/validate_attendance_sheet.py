# -*- coding: utf-8 -*-
from openerp import _, api, exceptions, fields, models
from openerp.exceptions import UserError, ValidationError


class ValidateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.validate"
    _description = """Check the user name and validate sheet.
    Useless for users in group_cooperative_admin"""
    _inherit = ["barcodes.barcode_events_mixin"]

    barcode = fields.Char(string="Barcode", required=True)
    annotation = fields.Text(
        "Important information requiring permanent member assistance",
        default="",
    )
    feedback = fields.Text("General feedback")
    worker_nb_feedback = fields.Selection(
        [
            ("not_enough", "Not enough"),
            ("enough", "Enough"),
            ("too_many", "Too many"),
        ],
        string="Number of workers",
        required=True,
    )

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode

    @api.multi
    def validate_sheet(self):
        sheet_id = self._context.get("active_id")
        sheet_model = self._context.get("active_model")
        sheet = self.env[sheet_model].browse(sheet_id)
        card = self.env["member.card"].search([("barcode", "=", self.barcode)])
        if not len(card):
            raise UserError(_("Please set a correct barcode."))
        partner = card[0].partner_id
        is_admin = partner.user_ids.has_group(
            "beesdoo_shift.group_cooperative_admin"
        )
        if not partner.super and not is_admin:
            raise UserError(
                _(
                    "Only super-cooperators and administrators can validate attendance sheets."
                )
            )
        if self.annotation:
            sheet.annotation += self.annotation
        if sheet.feedback:
            sheet.feedback += self.feedback
        sheet.worker_nb_feedback = self.worker_nb_feedback
        sheet.validate(partner or self.env.user.partner_id)
