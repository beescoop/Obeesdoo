from odoo import fields, models


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

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
        [("confirmed", "Confirmed"), ("cancelled", "Cancelled")],
        default="confirmed",
        required=True,
    )
    shift_id = fields.Many2one("volunteer.shift", "Shift", required=True)
    volunteer_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)
