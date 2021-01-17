import logging

from odoo import api, models, fields
from odoo import _

_logger = logging.getLogger(__name__)

class BeescoopPosOrder(models.Model):

    _inherit = 'pos.order'

    print_status = fields.Selection([('no_print', 'Do not Print'),
                                     ('to_print', 'To print'),
                                     ('printed', 'Printed')],
                                    default="no_print", string="Print Status")

    @api.model
    def send_order(self, receipt_name):
        order = self.search([('pos_reference', '=', receipt_name)])
        if not order:
            return _('Error: no order found')
        if not order.partner_id.email:
            return _('Cannot send the ticket, no email address found on the client')
        order.print_status = 'to_print'

        return _("Ticket will be sent")

    def _send_order_cron(self):
        mail_template = self.env.ref("beesdoo_pos_email_ticket.email_send_ticket")
        _logger.info("Start to send ticket")
        for order in self.search([('print_status', '=', 'to_print')]):
            if not order.partner_id.email:
                continue

            mail_template.send_mail(order.id, force_send=True)
            order.print_status = 'printed'
            #Make sure we commit the change to not send ticket twice
            self.env.cr.commit()

    def _get_taxes_amount(self):
        result = {}
        for l in self.lines:
            fpos = self.fiscal_position_id
            tax_ids_after_fiscal_position = fpos.map_tax(l.tax_ids, l.product_id, l.order_id.partner_id) if fpos else l.tax_ids
            price = l.price_unit * (1 - (l.discount or 0.0) / 100.0)
            taxes = tax_ids_after_fiscal_position.compute_all(price, self.pricelist_id.currency_id, l.qty, product=l.product_id, partner=self.partner_id)
            print(taxes)
            for t in taxes['taxes']:
                taxe = result.get(t['id'], {})
                taxe['name'] = t['name']
                taxe['amount'] = taxe.get('amount', 0) + t['amount']
                taxe['base'] = taxe.get('base', 0) + t['base']
                result[t['id']] = taxe
        return result.values()

