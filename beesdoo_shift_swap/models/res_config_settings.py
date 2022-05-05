from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    enable_solidarity = fields.Boolean(
        string="Activate solidarity offers and requests",
        config_parameter="beesdoo_shift.enable_solidarity",
    )
    percentage_presence = fields.Integer(
        string="Limit of percentage of presence of underpopulated shift",
        config_parameter="beesdoo_shift.percentage_presence",
    )
    day_limit_swap = fields.Integer(
        string="Number of day cooperator can swap his shift "
        "after the one he doesn't want",
        config_parameter="beesdoo_shift.day_limit_swap",
    )
    hours_limit_cancel_solidarity_offer = fields.Integer(
        string="Limit of hours to cancel a solidarity shift",
        config_parameter="beesdoo_shift.hours_limit_cancel_solidarity_offer",
    )
    solidarity_counter_start_value = fields.Integer(
        string="Start value of the global solidarity counter",
        config_parameter="beesdoo_shift.solidarity_counter_start_value",
        default=0,
    )
    solidarity_counter_limit = fields.Integer(
        string="Limit value of the global solidarity counter",
        config_parameter="beesdoo_shift.solidarity_counter_limit",
        default=0,
    )
    max_solidarity_requests_number = fields.Integer(
        string="Max number of solidarity requests per year",
        config_parameter="beesdoo_shift.max_solidarity_requests_number",
    )
