from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _prepare_invoice_line_from_po_line(self, line):
        """Override parent's method to set the invoice line description from the
        related purchase order line."""
        invoice_line = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line
        )
        if self.user_has_groups(
            "account_invoice_line_po_reference.group_invert_po_ref_on_inv_line"
        ):
            invoice_line["name"] = line.name + ": " + line.order_id.name
        return invoice_line
