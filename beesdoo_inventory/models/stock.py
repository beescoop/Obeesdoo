# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    max_shipping_date = fields.Datetime("End Shipping Date")
    responsible = fields.Many2one('res.partner', string="Responsible", default=lambda self: self.env.user.partner_id.id)

    def _add_follower(self):
        if(self.responsible):
            types = self.env['mail.message.subtype'].search(['|',('res_model','=','stock.picking'),('name','=','Discussions')])
            if not self.env['mail.followers'].search([('res_id', '=', self.id),
                                                      ('res_model', '=', 'stock.picking'),
                                                      ('partner_id', '=', self.responsible.id)]):
                self.env['mail.followers'].create({'res_model' : 'stock.picking',
                                            'res_id' : self.id, 
                                            'partner_id' : self.responsible.id,
                                            'subtype_ids': [(6, 0, types.ids)]})

    @api.multi
    def write(self, values):
        res = super(StockPicking, self).write(values)
        self._add_follower()
        return res

    @api.model
    def create(self, values):
        picking = super(StockPicking, self).create(values)
        picking._add_follower()
        return picking

    @api.multi
    def copy_qty(self):
        self.ensure_one()
        for pack_operation in self.pack_operation_product_ids:
            pack_operation.qty_done = pack_operation.product_qty
        return True