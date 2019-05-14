# -*- coding: utf-8 -*-

# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval
from openerp import fields, models, api

PARAMS = [
    ('irregular_shift_limit', 'beesdoo_website_shift.irregular_shift_limit'),
    ('highlight_rule_pc', 'beesdoo_website_shift.highlight_rule_pc'),
    ('hide_rule', 'beesdoo_website_shift.hide_rule'),
    ('irregular_enable_sign_up',
     'beesdoo_website_shift.irregular_enable_sign_up'),
    ('irregular_past_shift_limit',
     'beesdoo_website_shift.irregular_past_shift_limit'),
    ('regular_past_shift_limit',
     'beesdoo_website_shift.regular_past_shift_limit'),
    ('regular_next_shift_limit',
     'beesdoo_website_shift.regular_next_shift_limit'),
]


class WebsiteShiftConfigSettings(models.TransientModel):
    _name = 'beesdoo.website.shift.config.settings'
    _inherit = 'res.config.settings'

    # Irregular worker settings
    irregular_shift_limit = fields.Integer(
        help="Maximum shift that will be shown"
    )
    highlight_rule_pc = fields.Integer(
        help="Treshold (in %) of available space in a shift that trigger the "
             "highlight of the shift"
    )
    hide_rule = fields.Integer(
        help="Treshold ((available space)/(max space)) in percentage of "
             "available space under wich the shift is hidden"
    )
    irregular_enable_sign_up = fields.Boolean(
        help="Enable shift sign up for irregular worker"
    )
    irregular_past_shift_limit = fields.Integer(
        help="Maximum past shift that will be shown for irregular worker"
    )

    # Regular worker settings
    regular_past_shift_limit = fields.Integer(
        help="Maximum past shift that will be shown for regular worker"
    )
    regular_next_shift_limit = fields.Integer(
        help="Maximun number of next shift that will be shown"
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
            'irregular_shift_limit': int(
                self.env['ir.config_parameter']
                .get_param("beesdoo_website_shift.irregular_shift_limit")
            )
        }

    @api.multi
    def get_default_highlight_rule_pc(self):
        return {
            'highlight_rule_pc': int(
                self.env['ir.config_parameter']
                .get_param("beesdoo_website_shift.highlight_rule_pc")
            )
        }

    @api.multi
    def get_default_hide_rule(self):
        return {
            'hide_rule': int(self.env['ir.config_parameter'].get_param(
                'beesdoo_website_shift.hide_rule'))
        }

    @api.multi
    def get_default_irregular_shift_sign_up(self):
        return {
            'irregular_enable_sign_up':
                literal_eval(self.env['ir.config_parameter'].get_param(
                    'beesdoo_website_shift.irregular_enable_sign_up'))
        }

    @api.multi
    def get_default_irregular_past_shift_limit(self):
        return {
            'irregular_past_shift_limit': int(
                self.env['ir.config_parameter']
                .get_param("beesdoo_website_shift.irregular_past_shift_limit")
            )
        }

    @api.multi
    def get_default_regular_past_shift_limit(self):
        return {
            'regular_past_shift_limit': int(
                self.env['ir.config_parameter']
                .get_param('beesdoo_website_shift.regular_past_shift_limit')
            )
        }

    @api.multi
    def get_default_regular_next_shift_limit(self):
        return {
            'regular_next_shift_limit': int(
                self.env['ir.config_parameter']
                .get_param('beesdoo_website_shift.regular_next_shift_limit')
            )
        }
