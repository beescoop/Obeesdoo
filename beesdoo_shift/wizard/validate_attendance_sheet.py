# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import UserError, ValidationError


class ValidateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.validate"
    _description = """Check the user name and validate sheet.
    Useless for users in group_cooperative_admin"""
    _inherit = ["barcodes.barcode_events_mixin"]

    @api.multi
    def validate_sheet(self, user):
        sheet_id = self._context.get("active_id")
        sheet_model = self._context.get("active_model")
        sheet = self.env[sheet_model].browse(sheet_id)
        if not user.super:
            raise UserError(
                "Only super-cooperators and administrators can validate attendance sheets."
            )
        # Following methods call not working
        sheet.validated_by = user
        sheet.validate()

    def on_barcode_scanned(self, barcode):
        card = self.env["member.card"].search(
            [("barcode", "=", barcode)]
        )
        if not len(card):
            raise UserError("Please set a correct barcode.")
        self.validate_sheet(card[0].partner_id)
