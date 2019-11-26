# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _

from datetime import date, datetime, timedelta


class GenerateAttendanceSheet(models.TransientModel):
    _name = "beesdoo.shift.sheet.generate"
    _description = "Use a selected time range to generate the corresponding attendance sheet."

    time_range = fields.Selection("_get_time_ranges", string="Hours")

    def _get_time_ranges(self):
        time_ranges = set()
        tasks = self.env["beesdoo.shift.shift"]
        sheets = self.env["beesdoo.shift.sheet"]
        current_time = datetime.now()
        allowed_time_range = timedelta(minutes=45)

        tasks = tasks.search(
            [
                ("start_time", ">", str(current_time - allowed_time_range),),
                ("start_time", "<", str(current_time + allowed_time_range),),
            ]
        )

        for task in tasks:
            start_time = task.start_time
            end_time = task.end_time
            sheets = sheets.search(
                [("start_time", "=", start_time), ("end_time", "=", end_time),]
            )

            if len(sheets) == 0:
                start_time_dt = fields.Datetime.from_string(start_time)
                start_time_dt = fields.Datetime.context_timestamp(
                    self, start_time_dt
                )
                end_time_dt = fields.Datetime.from_string(end_time)
                end_time_dt = fields.Datetime.context_timestamp(
                    self, end_time_dt
                )

                # We display contextualized time range
                # but we save it according to UTC timezone
                time_ranges.add(
                    (
                        start_time + "~" + end_time,
                        start_time_dt.strftime("%H:%M")
                        + " - "
                        + end_time_dt.strftime("%H:%M"),
                    )
                )
        return list(time_ranges)

    @api.multi
    def button_generate(self):
        self.ensure_one()
        tasks = self.env["beesdoo.shift.shift"]
        sheets = self.env["beesdoo.shift.sheet"]
        if not self.time_range:
            raise exceptions.UserError(
                _("Please select a time time_range to generate the sheet.")
            )
        time_range = self.time_range.split("~")
        if len(time_range) != 2:
            raise exceptions.ValidationError(
                _("Selection key has wrong format.")
            )
        sheet = sheets.create(
            {"start_time": time_range[0], "end_time": time_range[1]}
        )

        return {
            "type": "ir.actions.act_window",
            "res_model": "beesdoo.shift.sheet",
            "res_id": sheet.id,
            "view_type": "form",
            "view_mode": "form",
        }
