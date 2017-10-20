# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

from datetime import timedelta

def add_days_delta(date_from, days_delta):
    if not date_from:
        return date_from
    next_date = fields.Date.from_string(date_from) + timedelta(days=days_delta)
    return fields.Date.to_string(next_date)

class ExemptReason(models.Model):
    _name = 'cooperative.exempt.reason'

    name = fields.Char(required=True)

class HistoryStatus(models.Model):
    _name = 'cooperative.status.history'

    _order= 'create_date desc'

    status_id = fields.Many2one('cooperative.status')
    cooperator_id = fields.Many2one('res.partner')
    change = fields.Char()
    type = fields.Selection([('status', 'Status Change'), ('counter', 'Counter Change')])
    user_id = fields.Many2one('res.users', string="User")

class CooperativeStatus(models.Model):
    _name = 'cooperative.status'
    _rec_name = 'cooperator_id'
    _order = 'cooperator_id'


    today = fields.Date(help="Field that allow to compute field and store them even if they are based on the current date")
    cooperator_id = fields.Many2one('res.partner')
    info_session = fields.Boolean('Information Session ?')
    info_session_date = fields.Datetime('Information Session Date')
    super = fields.Boolean("Super Cooperative")
    sr = fields.Integer("Compteur shift regulier", default=0)
    sc = fields.Integer("Compteur shift de compensation", default=0)
    time_extension = fields.Integer("Extension Days NB", default=0, help="Addtional days to the automatic extension, 5 mean that you have a total of 15 extension days of default one is set to 10")
    holiday_start_time = fields.Date("Holidays Start Day")
    holiday_end_time = fields.Date("Holidays End Day")
    alert_start_time = fields.Date("Alert Start Day")
    extension_start_time = fields.Date("Extension Start Day")
    #Champ compute
    working_mode = fields.Selection(
        [
            ('regular', 'Regular worker'),
            ('irregular', 'Irregular worker'),
            ('exempt', 'Exempted'),
        ],
        string="Working mode"
    )
    exempt_reason_id = fields.Many2one('cooperative.exempt.reason', 'Exempt Reason')
    status = fields.Selection([('ok',  'Up to Date'),
                               ('holiday', 'Holidays'),
                               ('alert', 'Alerte'),
                               ('extension', 'Extension'),
                               ('suspended', 'Suspended'),
                               ('unsubscribed', 'Unsubscribed')],
                              compute="_compute_status", string="Cooperative Status", store=True)
    can_shop = fields.Boolean(compute='_compute_status', store=True)
    history_ids = fields.One2many('cooperative.status.history', 'status_id', readonly=True)
    unsubscribed = fields.Boolean(default=False, help="Manually unsubscribed")



    @api.depends('today', 'sr', 'sc', 'holiday_end_time', 'holiday_start_time', 'time_extension', 'alert_start_time', 'extension_start_time', 'unsubscribed')
    def _compute_status(self):
        alert_delay = int(self.env['ir.config_parameter'].get_param('alert_delay', 28))
        grace_delay = int(self.env['ir.config_parameter'].get_param('default_grace_delay', 10))
        update = int(self.env['ir.config_parameter'].get_param('always_update', False))
        print update
        for rec in self:
            if update:
                rec.status = 'ok'
                rec.can_shop = True
                continue

            ok = rec.sr >= 0 and rec.sc >= 0
            grace_delay = grace_delay + rec.time_extension

            if rec.sr < -1 or rec.unsubscribed:
                rec.status = 'unsubscribed'
                rec.can_shop = False

            #Transition to alert sr < 0 or stay in alert sr < 0 or sc < 0 and thus alert time is defined
            elif not ok and rec.alert_start_time and rec.extension_start_time and rec.today <= add_days_delta(rec.extension_start_time, grace_delay):
                rec.status = 'extension'
                rec.can_shop = True
            elif not ok and rec.alert_start_time and rec.extension_start_time and rec.today > add_days_delta(rec.extension_start_time, grace_delay):
                rec.status = 'suspended'
                rec.can_shop = False
            elif not ok and rec.alert_start_time and rec.today > add_days_delta(rec.alert_start_time, alert_delay):
                rec.status = 'suspended'
                rec.can_shop = False
            elif (rec.sr < 0) or (not ok and rec.alert_start_time):
                rec.status = 'alert'
                rec.can_shop = True

            #Check for holidays; Can be in holidays even in alert or other mode ?
            elif rec.today >= rec.holiday_start_time and rec.today <= rec.holiday_end_time:
                rec.status = 'holiday'
                rec.can_shop = True
            elif ok or (not rec.alert_start_time and rec.sr >= 0):
                rec.status = 'ok'
                rec.can_shop = True


    @api.multi
    def write(self, vals):
        """
            Overwrite write to historize the change
        """
        for field in ['sr', 'sc', 'time_extension', 'extension_start_time', 'alert_start_time', 'unsubscribed']:
            if not field in vals:
                continue
            for rec in self:
                data = {
                        'status_id': rec.id,
                        'cooperator_id': rec.cooperator_id.id,
                        'type': 'counter',
                        'user_id': self.env.context.get('real_uid', self.env.uid),
                }
                if vals.get(field, rec[field]) != rec[field]:
                    data['change'] = '%s: %s -> %s' % (field.upper(), rec[field], vals.get(field))
                    self.env['cooperative.status.history'].sudo().create(data)
        return super(CooperativeStatus, self).write(vals)

    def _state_change(self, new_state, old_stage):
        self.ensure_one()
        if new_state == 'alert':
            self.write({'alert_start_time': self.today, 'extension_start_time': False, 'time_extension': 0})
        if new_state == 'ok': #reset alert start time if back to ok
            self.write({'alert_start_time': False, 'extension_start_time': False, 'time_extension': 0})
        if new_state == 'unsubscribed':
            self.cooperator_id.sudo().write({'subscribed_shift_ids' : [(5,0,0)]})
            self.env['beesdoo.shift.shift'].sudo().unsubscribe_from_today([self.cooperator_id.id], today=self.today)

    def _change_counter(self, data):
        self.sc += data.get('sc', 0)
        self.sr += data.get('sr', 0)

    @api.multi
    def _write(self, vals):
        """
            Overwrite write to historize the change of status
            and make action on status change
        """
        if 'status' in vals:
            self._cr.execute('select id, status, sr, sc from "%s" where id in %%s' % self._table, (self._ids,))
            result = self._cr.dictfetchall()
            old_status_per_id = {r['id'] : r for r in result}
            for rec in self:
                if old_status_per_id[rec.id]['status'] != vals['status']:
                    data = {
                        'status_id': rec.id,
                        'cooperator_id': rec.cooperator_id.id,
                        'type': 'status',
                        'change': "STATUS: %s -> %s" % (old_status_per_id[rec.id]['status'], vals['status']),
                        'user_id': self.env.context.get('real_uid', self.env.uid),
                    }
                    self.env['cooperative.status.history'].sudo().create(data)
                    rec._state_change(vals['status'], old_status_per_id[rec.id]['status'])
        return super(CooperativeStatus, self)._write(vals)

    _sql_constraints = [
        ('cooperator_uniq', 'unique (cooperator_id)', _('You can only set one cooperator status per cooperator')),
    ]

    @api.model
    def _set_today(self):
        """
            Method call by the cron to update store value base on the date
        """
        self.search([]).write({'today': fields.Date.today()})

    @api.multi
    def clear_history(self):
        self.ensure_one()
        self.history_ids.unlink()

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cooperative_status_ids = fields.One2many('cooperative.status', 'cooperator_id', readonly=True)
    super = fields.Boolean(related='cooperative_status_ids.super', string="Super Cooperative", readonly=True, store=True)
    info_session = fields.Boolean(related='cooperative_status_ids.info_session', string='Information Session ?', readonly=True, store=True)
    info_session_date = fields.Datetime(related='cooperative_status_ids.info_session_date', string='Information Session Date', readonly=True, store=True)
    working_mode = fields.Selection(related='cooperative_status_ids.working_mode', readonly=True, store=True)
    exempt_reason_id = fields.Many2one(related='cooperative_status_ids.exempt_reason_id', readonly=True, store=True)
    state = fields.Selection(related='cooperative_status_ids.status', readonly=True, store=True)
    extension_start_time = fields.Date(related='cooperative_status_ids.extension_start_time', string="Extension Start Day", readonly=True, store=True)
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

    @api.multi
    def coop_unsubscribe(self):
        res = self.coop_subscribe()
        res['context'] = {'default_unsubscribed': True}
        return res

    @api.multi
    def manual_extension(self):
        return {
           'name': _('Manual Extension'),
           'type': 'ir.actions.act_window',
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'beesdoo.shift.extension',
           'target': 'new',
        }

    @api.multi
    def auto_extension(self):
        res = self.manual_extension()
        res['context'] = {'default_auto': True}
        res['name'] = _('Trigger Grace Delay')
        return res

    @api.multi
    def register_holiday(self):
        return {
           'name': _('Register Holiday'),
           'type': 'ir.actions.act_window',
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'beesdoo.shift.holiday',
           'target': 'new',
        }

    #TODO access right + vue on res.partner
    #TODO can_shop : Status can_shop ou extempted ou part C
