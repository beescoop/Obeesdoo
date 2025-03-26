from odoo import api, fields, models


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

    name = fields.Char(compute="_compute_name")
    registration_date = fields.Datetime(default=fields.datetime.now(), required=True)
    registration_type = fields.Selection(
        [
            ("during_shift", "During-shift"),
            ("manual", "Manual"),
            ("recurrent", "Recurrent"),
            ("website", "Website"),
        ],
        default="manual",
        required=True,
    )
    registration_state = fields.Selection(
        [("confirmed", "Confirmed"), ("cancelled", "Cancelled")], default="confirmed"
    )
    shift_id = fields.Many2one("volunteer.shift", "Shift", required=True)
    volunteer_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)
    replaced_volunteer_id = fields.Many2one(
        "volunteer.volunteer", "Replaced By", required=False
    )

    @api.depends("shift_id.start_time", "shift_id.end_time", "shift_id.name")
    def _compute_name(self):
        for participation in self:
            participation.name = f"{participation.shift_id.name}#{participation.id}"
