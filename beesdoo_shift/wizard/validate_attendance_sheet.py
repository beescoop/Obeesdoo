# -*- coding: utf-8 -*-

import ast

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError


class ValidateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.validate"
    _description = """Check the user name and validate sheet.
    Useless for users in group_cooperative_admin"""
    _inherit = ["barcodes.barcode_events_mixin"]

    @api.multi
    def _get_active_sheet(self):
        sheet_id = self._context.get("active_id")
        sheet_model = self._context.get("active_model")

        if sheet_id and sheet_model:
            return self.env[sheet_model].browse(sheet_id)

    def _get_card_support_setting(self):
        return ast.literal_eval(
            self.env["ir.config_parameter"].get_param(
                "beesdoo_shift.card_support"
            )
        )

    @api.multi
    def _get_warning_regular_workers(self):
        """
        A warning is shown if some regular workers were not expected
        but should be doing their regular shifts. This warning is added
        to sheet's notes at validation.
        """
        sheet = self.active_sheet
        warning_message = ""
        if sheet:
            for added_shift in sheet.added_shift_ids:
                is_regular_worker = (
                    added_shift.worker_id.working_mode == "regular"
                )
                is_compensation = added_shift.is_compensation

                if is_regular_worker and not is_compensation:
                    warning_message += (
                        _(
                            "\n%s attended its shift as a normal one but was not expected. "
                            "Something may be wrong in his/her personnal informations.\n"
                        )
                        % added_shift.worker_id.name
                    )
        return warning_message

    active_sheet = fields.Many2one(
        "beesdoo.shift.sheet", default=_get_active_sheet
    )
    card_support = fields.Boolean(default=_get_card_support_setting)
    login = fields.Char(string="Login")
    password = fields.Char(string="Password")
    barcode = fields.Char(string="Barcode")
    warning_regular_workers = fields.Text(
        "Warning",
        default=_get_warning_regular_workers,
        help="Is any regular worker doing its regular shift as an added one ?",
    )
    notes = fields.Text(related="active_sheet.notes")
    feedback = fields.Text(related="active_sheet.feedback")
    worker_nb_feedback = fields.Selection(
        related="active_sheet.worker_nb_feedback", required=True
    )

    def on_barcode_scanned(self, barcode):
        self.barcode = barcode

    @api.multi
    def save(self):
        sheet = self.active_sheet
        sheet.notes = self.notes
        sheet.feedback = self.feedback
        sheet.worker_nb_feedback = self.worker_nb_feedback

    @api.multi
    def validate_sheet(self):
        sheet = self.active_sheet

        if self.card_support:
            # Login with barcode
            card = self.env["member.card"].search(
                [("barcode", "=", self.barcode)]
            )
            if not len(card):
                raise UserError(_("Please set a correct barcode."))
            partner = card[0].partner_id
        else:
            # Login with credentials
            if not self.login:
                raise UserError(_("Please enter your login."))
            user = self.env["res.users"].search([("login", "=", self.login)])
            user.sudo(user.id).check_credentials(self.password)
            partner = user.partner_id

        is_admin = partner.user_ids.has_group(
            "beesdoo_shift.group_cooperative_admin"
        )

        if not partner.super and not is_admin:
            raise UserError(
                _(
                    "Only super-cooperators and administrators can validate attendance sheets."
                )
            )

        self.notes += self.warning_regular_workers
        self.save()
        sheet._validate(partner or self.env.user.partner_id)
