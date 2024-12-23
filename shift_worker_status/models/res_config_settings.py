from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    irregular_penalty = fields.Boolean(
        string="Penalty for irregular worker with negative counter",
        help="""When selected, the irregular worker's counter will decrease
        by two when at zero or below, unless they were in alert
        before or were already penalized.""",
        config_parameter="shift_worker_status.irregular_penalty",
    )
