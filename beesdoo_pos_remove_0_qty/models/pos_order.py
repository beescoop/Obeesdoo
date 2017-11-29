# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order(self, order):
        lines = order['lines']
        order['lines'] = [l for l in lines if l[2]['qty'] !=0]
                
        return super(PosOrder, self)._process_order(order)