from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    max_shift_per_day = fields.Integer(
        string="Maximum number of shifts per day for one cooperator",
        config_parameter="beesdoo_shift.max_shift_per_day",
    )
    max_shift_per_month = fields.Integer(
        string="Maximum number of shifts per month for one cooperator",
        config_parameter="beesdoo_shift.max_shift_per_month",
    )
    enable_exchanges = fields.Boolean(
        string="Activate shift swaps and exchanges",
        config_parameter="beesdoo_shift.enable_exchanges",
    )
    percentage_presence = fields.Integer(
        string="Limit of percentage of presence of underpopulated shift",
        config_parameter="beesdoo_shift.percentage_presence",
    )
    day_limit_swap = fields.Integer(
        string="Number of days above which a cooperator cannot swap his shift",
        config_parameter="beesdoo_shift.day_limit_swap",
    )
    day_limit_request_exchange = fields.Integer(
        string="Number of days below which a cooperator cannot request"
        "an exchange with another cooperator",
        config_parameter="beesdoo_shift.day_limit_request_exchange",
    )
    day_limit_ask_for_exchange = fields.Integer(
        string="Number of days above which a cooperator cannot select shifts"
        "to exchange with one of his/hers",
        config_parameter="beesdoo_shift.day_limit_ask_for_exchange",
    )
    day_limit_exchange_with_same_timeslot = fields.Integer(
        string="Number of days below which a cooperator can only request exchanges"
        "with cooperators from the same timesolt in other weeks",
        config_parameter="beesdoo_shift.day_limit_exchange_with_same_timeslot",
    )
    enable_solidarity = fields.Boolean(
        string="Activate solidarity offers and requests",
        config_parameter="beesdoo_shift.enable_solidarity",
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
