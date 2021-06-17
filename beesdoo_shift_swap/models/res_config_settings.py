from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    percentage_presence = fields.Integer(
        string="Limit of percentage of presence of underpopulated shift",
        config_parameter="beesdoo_shift.percentage_presence",
    )
    day_limit_swap = fields.Integer(
        string=(
            "Number of day cooperator can swap his shift after the one he "
            "doesn't want"
        ),
        config_parameter="beesdoo_shift.day_limit_swap",
    )
