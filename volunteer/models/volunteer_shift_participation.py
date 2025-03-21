from odoo import api, fields, models


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

    name = fields.Char(compute="_compute_name")
    registration_date = fields.Datetime(default=fields.datetime.now(), required=True)
    registration_type = fields.Selection(
        [
            ("recurrent", "Recurrent"),
            ("website", "Website"),
            ("during_shift", "During-shift"),
        ],
        required=True,
    )
    registration_state = fields.Selection(
        [("confirmed", "Confirmed"), ("cancelled", "Cancelled")], default="confirmed"
    )
    shift_id = fields.Many2one("volunteer.shift", "Shift", required=True)
    volunteer_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)
    replaced_volunteer_id = fields.Many2one(
        "volunteer.volunteer", "Replaced Volunteer", required=False
    )

    @api.depends("shift_id.start_time", "shift_id.end_time", "shift_id.name")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.shift_id.name}#{record.id}"
