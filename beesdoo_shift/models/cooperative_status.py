# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class CooperativeStatus(models.Model):
    _name = 'cooperative.status'
    _rec_name = 'cooperator_id'

    cooperator_id = fields.Many2one('res.partner')
    info_session = fields.Boolean('Information Session ?')
    info_session_date = fields.Datetime('Information Session Date')
    super = fields.Boolean("Super Cooperative")
    sr = fields.Integer("Compteur shift regulier")
    sc = fields.Integer("Compteur shift de compensation")
    time_holiday = fields.Integer("Holidays Days NB", default=0)
    time_extension = fields.Integer("Extension Days NB", default=0) #Durée initial par défault sur ir_config_parameter
    holiday_start_time = fields.Date("Holidays Start Day")
    alert_start_time = fields.Date("Alert Start Day")
    extension_start_time = fields.Date("Extension Start Day")
    #Champ compute
    status = fields.Selection([('ok',  'Up to Date'), ('holiday', 'Holidays'), ('alert', 'Alerte'), ('unsubscribed', 'Unsubscribed')], compute="_compute_status", string="Cooperative Status")
    working_mode = fields.Selection(
        [
            ('regular', 'Regular worker'),
            ('irregular', 'Irregular worker'),
            ('exempt', 'Exempted'),
        ],
        string="Working mode",
    )

    def _compute_status(self):
        for rec in self:
            rec.status = 'ok'

    _sql_constraints = [
        ('cooperator_uniq', 'unique (cooperator_id)', _('You can only set one cooperator status per cooperator')),
    ]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cooperative_status_ids = fields.One2many('cooperative.status', 'cooperator_id', readonly=True)
    super = fields.Boolean(related='cooperative_status_ids.super', string="Super Cooperative", readonly=True, store=True)
    info_session = fields.Boolean(related='cooperative_status_ids.info_session', string='Information Session ?', readonly=True, store=True)
    info_session_date = fields.Datetime(related='cooperative_status_ids.info_session_date', string='Information Session Date', readonly=True, store=True)
    working_mode = fields.Selection(related='cooperative_status_ids.working_mode', readonly=True, store=True)
    subscribed_shift_ids = fields.Many2many('beesdoo.shift.template')
    @api.multi
    def coop_subscribe(self):
        return {
           'name': _('Subscribe Cooperator'),
           'type': 'ir.actions.act_window',
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'beesdoo.shift.subscribe',
           'target': 'new',
        }

    #TODO access right + vue on res.partner
