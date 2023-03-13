from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    share_supercoop_info = fields.Boolean(
        string="Accept to share my info as Supercoop",
        default=False,
    )
