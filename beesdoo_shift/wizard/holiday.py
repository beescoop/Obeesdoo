from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Subscribe(models.TransientModel):
    _name = "beesdoo.shift.holiday"
    _description = "beesdoo.shift.holiday"
    _inherit = "beesdoo.shift.action_mixin"

    holiday_start_day = fields.Date(
        string="Start date for the holiday", default=fields.Date.today
    )
    holiday_end_day = fields.Date(string="End date for the holiday (included)")

    @api.multi
    def holidays(self):
        self = self._check()  # maybe a different group
        status_id = self.env["cooperative.status"].search(
            [("cooperator_id", "=", self.cooperator_id.id)]
        )
        if (
            status_id.holiday_end_time
            and status_id.holiday_end_time >= status_id.today
        ):
            raise ValidationError(
                _(
                    "You cannot encode new holidays since the previous "
                    "holidays encoded are not over yet "
                )
            )
        status_id.sudo().write(
            {
                "holiday_start_time": self.holiday_start_day,
                "holiday_end_time": self.holiday_end_day,
            }
        )
        self.env["beesdoo.shift.shift"].sudo().unsubscribe_from_today(
            [self.cooperator_id.id],
            today=self.holiday_start_day,
            end_date=self.holiday_end_day,
        )
