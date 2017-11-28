# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
#          Julien Weste (julien.weste@akretion.com.br)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.multi
    def write(self, vals):
        if 'qty' in vals.keys() and vals['qty'] == 0:
            self.unlink()
        else:
            super(PosOrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        pol = super(PosOrderLine, self).create(vals)
        if pol.qty == 0:
            pol.unlink()
        return pol
