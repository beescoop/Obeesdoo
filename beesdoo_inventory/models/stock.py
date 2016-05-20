# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    max_shipping_date = fields.Datetime("End Shipping Date")
    responsible = fields.Many2one("res.partner", string="Responsible Person")

    def _add_follower(self):
        self.env['mail.followers'].create({'partner_id': self.responsible.id,
                                           'res_id': self.id,
                                           'res_model': "stock.picking",})

    @api.multi
    def write(self, values):
        res = super(StockPicking, self).write(values)
        print "WRITE"
        print values.get('responsible')
        if values.get('responsible'):
            for picking in self:
                picking._add_follower()
        return res

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        picking._add_follower()
        return picking