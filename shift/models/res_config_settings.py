from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    shift_period = fields.Integer(
        string="Shift period", config_parameter="shift.shift_period"
    )

    min_hours_to_unsubscribe = fields.Integer(
        string="Minimum number of hours before a shift to unsubscribe",
        config_parameter="shift.min_hours_to_unsubscribe",
    )
    max_shift_per_day = fields.Integer(
        string="Maximum number of shifts per day for one cooperator",
        config_parameter="shift.max_shift_per_day",
    )
    max_shift_per_month = fields.Integer(
        string="Maximum number of shifts per month for one cooperator",
        config_parameter="shift.max_shift_per_month",
    )
