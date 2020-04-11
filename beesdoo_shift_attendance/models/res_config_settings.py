# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    card_support = fields.Boolean(
        string="Scan cooperators cards instead of login for sheets validation",
        config_parameter="beesdoo_shift.card_support",
    )
    task_type_default_id = fields.Many2one(
        "beesdoo.shift.type",
        string="Default Task Type",
        help="Default task type for attendance sheet pre-filling",
        required=True,
        default=False,
    )
    attendance_sheet_generation_interval = fields.Integer(
        string="Time interval for attendance sheet generation",
        help="Time interval expressed in minutes",
        required=True,
        config_parameter="beesdoo_shift.attendance_sheet_generation_interval",
    )

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param(
            "beesdoo_shift.card_support", str(self.card_support),
        )
        parameters.set_param(
            "beesdoo_shift.task_type_default_id",
            str(self.task_type_default_id.id),
        )
        parameters.set_param(
            "beesdoo_shift.attendance_sheet_generation_interval",
            str(self.attendance_sheet_generation_interval),
        )

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            card_support=ast.literal_eval(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.card_support"
                ),
            ),
            task_type_default_id=int(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.task_type_default_id"
                )
            ),
        )
        return res
