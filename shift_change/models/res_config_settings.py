from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # enable_exchanges
    enable_shift_changes = fields.Boolean(
        string="Activate shift changes",
        config_parameter="shift_change.enable_shift_changes",
    )
    # day_limit_swap
    hour_limit_change = fields.Integer(
        string="Number of hours above which a cooperator cannot change his shift",
        config_parameter="shift_change.hour_limit_change",
    )
