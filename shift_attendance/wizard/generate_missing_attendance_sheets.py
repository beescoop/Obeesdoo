from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class GenerateMissingAttendanceSheets(models.TransientModel):
    """
    Generate missing past sheets
    """

    _name = "beesdoo.shift.generate_missing_attendance_sheets"
    _description = "beesdoo.shift.generate_missing_attendance_sheets"

    date_start = fields.Datetime("Start date", required=True)
    date_end = fields.Datetime("End date", required=True)

    @api.multi
    def generate_missing_attendance_sheets(self):
        self.ensure_one()
        tasks = self.env["beesdoo.shift.shift"]
        sheets = self.env["beesdoo.shift.sheet"]

        tasks = tasks.search(
            [
                ("start_time", ">", self.date_start),
                ("start_time", "<", self.date_end),
            ]
        )

        # We should not loop on task with same start_time and end_time
        # To improve performances
        for task in tasks:
            start_time = task.start_time
            end_time = task.end_time
            sheet = sheets.search(
                [("start_time", "=", start_time), ("end_time", "=", end_time)]
            )

            if not sheet:
                sheets |= sheets.create(
                    {"start_time": start_time, "end_time": end_time}
                )

        return {
            "name": _("Generated Missing Sheets"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "beesdoo.shift.sheet",
            "target": "current",
            "domain": [("id", "in", sheets.ids)],
        }

    @api.constrains("date_start", "date_end")
    def constrains_dates(self):
        if self.date_start > datetime.now() or self.date_end > datetime.now():
            raise UserError(_("Only past attendance sheets can be generated"))
