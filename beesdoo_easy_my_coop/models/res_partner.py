# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    share_type = fields.Selection(compute='_get_share_product_type')

    @api.multi
    @api.depends('share_ids', 'share_ids.share_product_id', 'share_ids.share_product_id.default_code')
    def _get_share_product_type(self):
        for rec in self:
            codes = rec.share_ids.mapped('share_product_id.default_code')
            rec.share_type = codes[0] if codes else ''