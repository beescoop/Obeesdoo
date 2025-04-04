from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Participation(models.Model):
    _name = "volunteer.shift.participation"
    _description = "Shift participation"

    registration_date = fields.Datetime(default=fields.datetime.now(), required=True)
    cancellation_date = fields.Datetime(
        compute="_compute_cancellation_date", store=True
    )
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
        [("confirmed", "Confirmed"), ("canceled", "canceled")],
        default="confirmed",
        required=True,
    )
    shift_id = fields.Many2one("volunteer.shift", "Shift", required=True)
    volunteer_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)

    @api.depends("registration_state")
    def _compute_cancellation_date(self):
        for participation in self:
            if participation.registration_state == "canceled":
                participation.cancellation_date = fields.datetime.now()

    @api.constrains("shift_id", "registration_state")
    def _check_remaining_slots(self):
        for participation in self:
            availability = self.shift_id.can_accept_participation()
            if not availability["can_accept"]:
                nb_confirmed_volunteers = availability["nb_confirmed_volunteers"]
                raise ValidationError(
                    _(
                        f"It is not possible to register"
                        f" {nb_confirmed_volunteers} volunteers in this shift."
                        f" The maximum capacity is {participation.shift_id.max_volunteer_nb}."
                    )
                )
