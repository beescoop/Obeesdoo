# -*- coding: utf-8 -*-

# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from openerp import fields, models, api


class ShiftConfigSettings(models.TransientModel):
    _name = "beesdoo.shift.config.settings"
    _inherit = "res.config.settings"

    card_support = fields.Boolean(
        string="Scan cooperators cards instead of login for sheets validation",
        default=False,
    )
    default_task_type_id = fields.Many2one(
        "beesdoo.shift.type",
        string="Default Task Type",
        help="Default task type for attendance sheet pre-filling",
        required=True,
    )
    attendance_sheet_generation_interval = fields.Integer(
        string="Time interval for attendance sheet generation",
        help="Time interval expressed in minutes",
        required=True,
    )

    @api.multi
    def set_params(self):
        self.ensure_one()
        parameters = self.env["ir.config_parameter"]
        parameters.set_param(
            "beesdoo_shift.card_support", str(self.card_support),
        )
        parameters.set_param(
            "beesdoo_shift.default_task_type_id",
            str(self.default_task_type_id.id),
        )
        parameters.set_param(
            "beesdoo_shift.attendance_sheet_generation_interval",
            str(self.attendance_sheet_generation_interval),
        )

    @api.multi
    def get_default_card_support(self):
        return {
            "card_support": ast.literal_eval(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.card_support"
                )
            )
        }

    @api.multi
    def get_default_task_type_id(self):
        return {
            "default_task_type_id": int(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.default_task_type_id"
                )
            )
        }

    @api.multi
    def get_default_attendance_sheet_generation_interval(self):
        return {
            "attendance_sheet_generation_interval": int(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.attendance_sheet_generation_interval"
                )
            )
        }
