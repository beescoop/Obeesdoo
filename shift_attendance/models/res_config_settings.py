# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    card_support = fields.Boolean(
        string="Scan cooperators cards instead of login for sheets validation",
        config_parameter="beesdoo_shift_attendance.card_support",
    )
    pre_filled_task_type_id = fields.Many2one(
        comodel_name="beesdoo.shift.type",
        string="Default Task Type",
        help="Default task type for attendance sheet pre-filling",
        required=True,
        config_parameter="beesdoo_shift_attendance.pre_filled_task_type_id",
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
    attendance_sheet_default_shift_state = fields.Selection(
        [
            ("done", "Present"),
            ("absent_0", "Absent - 0 Compensation"),
            ("absent_1", "Absent - 1 Compensation"),
            ("absent_2", "Absent - 2 Compensations"),
        ],
        string="Default Shift State",
        required=True,
        config_parameter=(
            "beesdoo_shift_attendance.attendance_sheet_default_shift_state"
        ),
        help="Default state set for shifts on attendance sheets",
    )
