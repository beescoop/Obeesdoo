from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Subscribe(models.TransientModel):
    _name = "beesdoo.shift.holiday"
    _description = "beesdoo.shift.holiday"
    _inherit = "beesdoo.shift.action_mixin"

    def _get_cooperative_status(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return partner_id.cooperative_status_ids

    def _get_holiday_start_day(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return (
            partner_id.cooperative_status_ids.holiday_start_time or fields.Date.today()
        )

    def _get_holiday_end_day(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return partner_id.cooperative_status_ids.holiday_end_time

    status_id = fields.Many2one("cooperative.status", default=_get_cooperative_status)
    holiday_start_day = fields.Date(
        string="Start date for the holiday", default=_get_holiday_start_day
    )
    holiday_end_day = fields.Date(
        string="End date for the holiday (included)",
        default=_get_holiday_end_day,
    )

    @api.multi
    def holidays(self):
        self = self._check()  # maybe a different group
        if (
            self.holiday_start_day != self.status_id.holiday_start_time
            and self.status_id.holiday_start_time
            and self.status_id.holiday_start_time <= self.status_id.today
            and self.status_id.holiday_end_time
            and self.status_id.holiday_end_time >= self.status_id.today
        ):
            raise ValidationError(
                _("You cannot edit start date of an holiday that is not over yet.")
            )
        if (
            self.holiday_start_day != self.status_id.holiday_start_time
            and self.holiday_start_day <= self.status_id.today
        ):
            raise ValidationError(
                _(
                    "You cannot encode a start date that is in the past "
                    "(including today)."
                )
            )
        if (
            self.holiday_end_day != self.status_id.holiday_end_time
            and self.holiday_end_day <= self.status_id.today
        ):
            raise ValidationError(
                _(
                    "You cannot encode a end date that is in the past "
                    "(including today)."
                )
            )
        self.status_id.sudo().write(
            {
                "holiday_start_time": self.holiday_start_day,
                "holiday_end_time": self.holiday_end_day,
            }
        )
