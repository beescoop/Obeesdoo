# -*- coding: utf-8 -*-

from openerp import fields, models, api

PARAMS = [
    ('irregular_shift_limit', 'beesdoo_website_shift.irregular_shift_limit'),
    ('highlight_rule', 'beesdoo_website_shift.highlight_rule'),
    ('hide_rule', 'beesdoo_website_shift.hide_rule'),
]

class WebsiteShiftConfigSettings(models.TransientModel):

    _name = 'beesdoo.website.shift.config.settings'
    _inherit = 'res.config.settings'

    irregular_shift_limit = fields.Integer(
        help="Maximum shift that will be shown"
    )
    highlight_rule = fields.Integer(
        help="Treshold of available space in a shift that trigger the highlight of the shift"
    )
    hide_rule = fields.Integer(
        help="Treshold ((available space)/(max space)) in percentage of available space under wich the shift is hidden"
    )

    @api.multi
    def set_params(self):
        self.ensure_one()

        for field_name, key_name in PARAMS:
            value = getattr(self, field_name)
            self.env['ir.config_parameter'].set_param(key_name, str(value))

    @api.multi
    def get_default_irregular_shift_limit(self):
        return {
            'irregular_shift_limit': int(self.env['ir.config_parameter'].get_param(
                'beesdoo_website_shift.irregular_shift_limit'))
        }

    @api.multi
    def get_default_highlight_rule(self):
        return {
            'highlight_rule': int(self.env['ir.config_parameter'].get_param('beesdoo_website_shift.highlight_rule'))
        }

    @api.multi
    def get_default_hide_rule(self):
        return {
            'hide_rule': int(self.env['ir.config_parameter'].get_param('beesdoo_website_shift.hide_rule'))
        }
