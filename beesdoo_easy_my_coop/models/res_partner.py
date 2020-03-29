from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    can_shop = fields.Boolean(compute='_can_shop', store=True)
    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session",
        default=False,
    )

    @api.depends('cooperator_type',
                 'cooperative_status_ids',
                 'cooperative_status_ids.can_shop')
    def _can_shop(self):
        product_obj = self.env['product.template']
        can_shop_shares = product_obj.search([('is_share', '=', True),
                                              ('can_shop', '=', True)
                                              ]).mapped('default_code')
        for rec in self:
            if rec.cooperator_type in can_shop_shares:
                rec.can_shop = True
            elif (rec.cooperative_status_ids
                  and rec.cooperative_status_ids[0].can_shop):
                rec.can_shop = True
            else:
                rec.can_shop = False
