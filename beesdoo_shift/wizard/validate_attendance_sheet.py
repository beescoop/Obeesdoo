# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import UserError, ValidationError


class ValidateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.validate"
    _description = """Check the user name and validate sheet.
    Useless for users in group_cooperative_admin"""

    def _get_sheet(self):
        return self._context.get("active_id")

    # current user as default value  !
    user = fields.Many2one("res.partner", string="User Name", required=True,)

    # Is the "@api.multi" correct here ?
    @api.multi
    def validate_sheet(self):
        sheet_id = self._context.get("active_id")
        sheet_model = self._context.get("active_model")
        sheet = self.env[sheet_model].browse(sheet_id)
        sheet.ensure_one()
        if not self.user.super:
            raise UserError(
                "You must be super-coop or admin to validate the sheet."
            )
        sheet.validated_by = self.user
        sheet.validate()

        return
