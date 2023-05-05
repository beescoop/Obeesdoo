from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_period = fields.Integer(
        string="Shift period", config_parameter="shift.shift_period"
    )
