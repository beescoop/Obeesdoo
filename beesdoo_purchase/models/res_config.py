from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_invert_po_ref_on_inv_line = fields.Boolean(
        """Allow inverting the Purchase Order Reference on the
        invoice lines""",
        implied_group="beesdoo_purchase."
        "group_invert_po_ref_on_inv_line",
        help="""Allows you to invert Purchase Order Reference on the
        invoice lines."""
    )
