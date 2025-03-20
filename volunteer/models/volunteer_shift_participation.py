from odoo import fields, models


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

    registration_date = fields.Datetime()
    registration_type = fields.Selection(
        [
            ("recurrent", "Recurrent"),
            ("website", "Website"),
            ("during_shift", "During-shift"),
        ]
    )
    registration_state = fields.Selection(
        [("confirmed", "confirmed"), ("cancelled", "Cancelled")], default="cancelled"
    )
