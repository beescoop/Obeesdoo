from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    request_number_limit = fields.Integer(
        string="Maximum number of requests (per category)"
        "displayed on page 'My requests'",
        config_parameter="beesdoo_website_shift_swap.request_number_limit",
    )
