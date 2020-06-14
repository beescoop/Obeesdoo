# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    card_support = fields.Boolean(
        string="Scan cooperators cards instead of login for sheets validation",
        config_parameter="beesdoo_shift_attendance.card_support",
    )
    pre_filled_task_type_id = fields.Many2one(
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
        config_parameter=(
            "beesdoo_shift_attendance.attendance_sheet_generation_interval"
        ),
    )

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        parameters = self.env["ir.config_parameter"].sudo()
        parameters.set_param(
            "beesdoo_shift_attendance.pre_filled_task_type_id",
            str(self.pre_filled_task_type_id.id),
        )

    @api.multi
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            pre_filled_task_type_id=int(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift_attendance.pre_filled_task_type_id"
                )
            )
        )
        return res
