from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TemporaryExemption(models.TransientModel):
    _name = "beesdoo.shift.temporary_exemption"
    _description = "beesdoo.shift.temporary_exemption"
    _inherit = "beesdoo.shift.action_mixin"

    def _get_cooperative_status(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return partner_id.cooperative_status_ids

    def _get_temporary_exempt_reason_id(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return partner_id.cooperative_status_ids.temporary_exempt_reason_id

    def _get_temporary_exempt_start_date(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return (
            partner_id.cooperative_status_ids.temporary_exempt_start_date
            or fields.Date.today()
        )

    def _get_temporary_exempt_end_date(self):
        partner_id = (
            self.env["res.partner"].browse(self._context.get("active_id")).exists()
        )
        return partner_id.cooperative_status_ids.temporary_exempt_end_date

    status_id = fields.Many2one("cooperative.status", default=_get_cooperative_status)
    temporary_exempt_reason_id = fields.Many2one(
        "cooperative.exempt.reason",
        "Exempt Reason",
        required=True,
        default=_get_temporary_exempt_reason_id,
    )
    temporary_exempt_start_date = fields.Date(
        default=_get_temporary_exempt_start_date, required=True
    )
    temporary_exempt_end_date = fields.Date(
        default=_get_temporary_exempt_end_date, required=True
    )

    @api.multi
    def exempt(self):
        self = self._check()  # maybe a different group
        if (
            self.temporary_exempt_start_date
            != self.status_id.temporary_exempt_start_date
            and self.status_id.temporary_exempt_start_date
            and self.status_id.temporary_exempt_start_date <= self.status_id.today
            and self.status_id.temporary_exempt_end_date
            and self.status_id.temporary_exempt_end_date >= self.status_id.today
        ):
            raise ValidationError(
                _("You cannot edit start date of an holiday that is not over yet.")
            )
        if (
            self.temporary_exempt_start_date
            != self.status_id.temporary_exempt_start_date
            and self.temporary_exempt_start_date <= self.status_id.today
        ):
            raise ValidationError(
                _(
                    "You cannot encode a start date that is in the past "
                    "(including today)."
                )
            )
        if (
            self.temporary_exempt_end_date != self.status_id.temporary_exempt_end_date
            and self.temporary_exempt_end_date <= self.status_id.today
        ):
            raise ValidationError(
                _(
                    "You cannot encode a end date that is in the past "
                    "(including today)."
                )
            )
        self.status_id.sudo().write(
            {
                "temporary_exempt_start_date": self.temporary_exempt_start_date,
                "temporary_exempt_end_date": self.temporary_exempt_end_date,
                "temporary_exempt_reason_id": (self.temporary_exempt_reason_id.id),
            }
        )
