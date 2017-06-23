# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    cooperator_type = fields.Selection(selection='_get_share_type', compute='_compute_share_type', string='Cooperator Type', store=True)

    @api.multi
    @api.depends('share_ids', 'share_ids.share_product_id', 'share_ids.share_product_id.default_code')
    def _compute_share_type(self):
        for rec in self:
            codes = rec.share_ids.mapped('share_product_id.default_code')
            rec.cooperator_type = codes[0] if codes else ''

    @api.multi
    def _get_share_type(self):
        share_type_list = [('','')]
        for share_type in self.env['product.product'].search([('is_share','=',True)]):
            share_type_list.append((share_type.default_code, share_type.short_name))
        return share_type_list

    @api.noguess
    def _auto_init(self, cr, context=None):
        cr.execute("ALTER TABLE res_partner DROP COLUMN IF EXISTS cooperator_type")
        res = super(Partner, self)._auto_init(cr, context=context)
        return res