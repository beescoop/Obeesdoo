# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import UserError, ValidationError


class ValidateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.validate"
    _description = """Check the user name and validate sheet.
    Useless for users in group_cooperative_admin"""

    #card = fields.Many2one("member.card", string="MemberCard")
    barcode = fields.Char(string="Barcode", required=True)
    user = fields.Many2one("res.partner", compute="_compute_user", string="User Name", readonly=True)

    @api.depends("barcode")
    def _compute_user(self):
        if self.barcode:
            card = self.env["member.card"].search([("barcode", "=", self.barcode)])
            if card:
                self.user = card[0].partner_id
            else:
                self.user = False

    # Is the "@api.multi" correct here ?
    @api.multi
    def validate_sheet(self):
        if not self.user:
            raise UserError("Please set a correct barcode.")
        sheet_id = self._context.get("active_id")
        sheet_model = self._context.get("active_model")
        sheet = self.env[sheet_model].browse(sheet_id)
        if not self.user.super:
            raise UserError(
                "You must be super-coop or admin to validate the sheet."
            )
        sheet.validated_by = self.user
        sheet.validate()

        return
