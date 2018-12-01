# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class BeesPOS(models.Model):
    _inherit = 'pos.config'

    bill_value = fields.One2many('bill_value', 'pos', copy=True)

class BillValue(models.Model):
    _name = 'bill_value'
    _order = 'name asc'

    name = fields.Float(string='Name')
    pos = fields.Many2one('pos.config')

class BeesAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.cashbox'

    def _get_default_line(self):
        if not self.env.context.get('active_id'):
            return []

        pos_session_rec = self.env['pos.session'].browse(self.env.context['active_id'])
        return [(0, 0, {'coin_value' : bill_value_rec.name, 'subtotal':0.0}) for bill_value_rec in pos_session_rec.config_id.bill_value]

    cashbox_lines_ids = fields.One2many(default=_get_default_line)

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

    @api.model
    def _send_order_cron(self):
        mail_template = self.env.ref("beesdoo_pos.email_send_ticket")
        _logger.info("Start to send ticket")
        for order in self.search([('print_status', '=', 'to_print')]):
            if not order.partner_id.email:
                continue

            mail_template.send_mail(order.id, force_send=True)
            order.print_status = 'printed'
            #Make sure we commit the change to not send ticket twice
            self.env.cr.commit()


class BeescoopPosPartner(models.Model):
    _inherit = 'res.partner'

    def _get_eater(self):
        eaters = [False, False, False]
        for i, eater in enumerate(self.child_eater_ids):
            eaters[i] = eater.name
        return tuple(eaters)

    @api.multi
    def get_eater(self):
        eater1, eater2, eater3 = self._get_eater()
        return eater1, eater2, eater3

from openerp.addons.point_of_sale.report import pos_receipt

class order_tva_included(pos_receipt.order):

    def __init__(self, cr, uid, name, context):
        super(order_tva_included, self).__init__(cr, uid, name, context=context)
        self.env = api.Environment(cr, uid, context)

    def netamount(self, order_line_id):
        order_line = self.env['pos.order.line'].browse(order_line_id)
        if order_line.order_id.config_id.iface_tax_included:
            return order_line.price_subtotal_incl
        else:
            return order_line.price_subtotal


class report_order_receipt(models.AbstractModel):
    _inherit = 'report.point_of_sale.report_receipt'
    _template = 'point_of_sale.report_receipt'
    _wrapped_report_class = order_tva_included