# this file should be removed from the module after the deployment
from openupgradelib import openupgrade

from odoo.tools.convert import ParseError


def rename_security_group(cr):
    try:
        openupgrade.rename_xmlids(
            cr,
            [
                (
                    "beesdoo_purchase.group_invert_po_ref_on_inv_line",
                    "account_invoice_line_po_reference.group_invert_po_ref_on_inv_line",  # noqa
                )
            ],
        )
    except ParseError:
        pass
