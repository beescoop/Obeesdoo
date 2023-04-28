# Copyright 2017-2020 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    # Irregular worker settings
    irregular_shift_limit = fields.Integer(
        default=0,
        help="Maximum shift that will be shown"
    )
    highlight_rule_pc = fields.Integer(
        default=30,
        help="Treshold (in %) of available space in a shift that trigger the "
             "highlight of the shift"
    )
    hide_rule = fields.Integer(
        default=20,
        help="Treshold ((available space)/(max space)) in percentage of "
             "available space under wich the shift is hidden"
    )
    irregular_enable_sign_up = fields.Boolean(
        default=True,
        help="Enable shift sign up for irregular worker"
    )
    irregular_past_shift_limit = fields.Integer(
        default=10,
        help="Maximum past shift that will be shown for irregular worker"
    )

    # Regular worker settings
    regular_past_shift_limit = fields.Integer(
        default=10,
        help="Maximum past shift that will be shown for regular worker"
    )
    regular_next_shift_limit = fields.Integer(
        default=13,
        help="Maximun number of next shift that will be shown"
    )
    regular_highlight_rule = fields.Integer(
        default=20,
        help="Treshold (in %) of available space in a shift that trigger the "
        "the highlight of a shift template."
    )
