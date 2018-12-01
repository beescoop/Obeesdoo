# -*- coding: utf-8 -*-
from openerp import models, api, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    manual_date_planned = fields.Datetime(string='Scheduled Date', required=True)

    @api.onchange('order_line', 'order_line.date_planned')
    def _on_change_manual_date_planned(self):
        """
            Since we don't see the date planned on the line anymore
            give an idea of the user by setting the first date planned of the lines
        """
        for line in self.order_line:
            if line.date_planned and not self.manual_date_planned:
                self.manual_date_planned = line.date_planned
                break;

    @api.multi
    def button_confirm(self):
        """
            Since we hide the button to set the date planned on all line and we 
            hide them, we call the method to set the date planned on the line at the confirmation
        """
        self.ensure_one()
        self.with_context(date_planned=self.manual_date_planned).action_set_date_planned()
        return super(PurchaseOrder, self).button_confirm()
