from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        super(AccountInvoice,self)._compute_residual()
        sign = self.amount_total < 0 and -1 or 1
        self.residual_company_signed *= sign
        self.residual_signed *= sign
        self.residual *= sign

    @api.multi
    def action_invoice_open(self):
        if self.user_has_groups(
            "beesdoo_account." "group_validate_invoice_negative_total_amount"
        ):
            return self.action_invoice_negative_amount_open()
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_invoice_negative_amount_open(self):
        """Identical to action_invoice_open without UserError on an invoice with a negative total amount"""
        to_open_invoices = self.filtered(lambda inv: inv.state != "open")
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(
                _(
                    "The field Vendor is required, please complete it to validate the Vendor Bill."
                )
            )
        if to_open_invoices.filtered(lambda inv: inv.state != "draft"):
            raise UserError(
                _("Invoice must be in draft state in order to validate it.")
            )
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _(
                    "No account was found to create the invoice, be sure you have installed a chart of account."
                )
            )
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()
