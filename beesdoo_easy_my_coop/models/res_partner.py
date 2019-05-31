# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    cooperator_type = fields.Selection(selection='_get_share_type', compute='_compute_share_type', string='Cooperator Type', store=True)
    can_shop = fields.Boolean(compute='_can_shop', store=True)
    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session",
        default=False,
    )

    @api.depends('cooperator_type', 'cooperative_status_ids', 'cooperative_status_ids.can_shop')
    def _can_shop(self):
        for rec in self:
            if rec.cooperator_type == 'share_b':
                rec.can_shop = True
            elif rec.cooperative_status_ids and rec.cooperative_status_ids[0].can_shop:
                rec.can_shop = True
            else:
                rec.can_shop = False


    @api.multi
    @api.depends('share_ids', 'share_ids.share_product_id', 'share_ids.share_product_id.default_code', 'share_ids.share_number')
    def _compute_share_type(self):
        for rec in self:
            if rec.share_ids and rec.share_ids[0].share_number > 0:
                rec.cooperator_type = rec.share_ids[0].share_product_id.default_code
            else:
                rec.cooperator_type = ''

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