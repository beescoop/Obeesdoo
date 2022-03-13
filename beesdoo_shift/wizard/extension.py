from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Subscribe(models.TransientModel):
    _name = "beesdoo.shift.extension"
    _description = "beesdoo.shift.extension"
    _inherit = "beesdoo.shift.action_mixin"

    def _get_default_extension_delay(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_extension_delay", 28)
        )

    extension_start_date = fields.Date(
        string="Start date for the extension",
        default=fields.Date.today,
        readonly=True,
    )
    auto = fields.Boolean("Auto Extension", default=False)
    extension_days = fields.Integer(default=_get_default_extension_delay)

    @api.multi
    def auto_ext(self):
        self = self._check(group="beesdoo_shift.group_shift_attendance")
        status_id = self.env["cooperative.status"].search(
            [("cooperator_id", "=", self.cooperator_id.id)]
        )
        status_id.sudo().write({"extension_start_time": self.extension_start_date})

    @api.multi
    def extension(self):
        self = self._check()  # maybe a different group
        grace_delay = int(
            self.env["ir.config_parameter"].sudo().get_param("default_grace_delay", 10)
        )
        status_id = self.env["cooperative.status"].search(
            [("cooperator_id", "=", self.cooperator_id.id)]
        )
        if not status_id.extension_start_time:
            raise UserError(
                _(
                    "You should not make a manual extension when the grace "
                    "delay has not been triggered yet "
                )
            )
        today_delay = (
            status_id.today - status_id.extension_start_time
        ).days - grace_delay
        if today_delay < 0:
            raise UserError(
                _("You should not start a manual extension during the grace delay ")
            )
        status_id.sudo().write({"time_extension": self.extension_days + today_delay})
