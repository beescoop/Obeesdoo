from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)
PERIOD = 28  # TODO: use system parameter

def add_days_delta(date_from, days_delta):
    if not date_from:
        return date_from
    next_date = date_from + timedelta(days=days_delta)
    return next_date

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

    def get_status_value(self):
        """
        Workararound to get translated selection value instead of key in mail template.
        """

        state_list = self.env["cooperative.status"]._fields["status"].selection
        state_list = self.env["cooperative.status"]._fields['status']._description_selection(self.env)

        return dict(state_list)[self.status]

    today = fields.Date(help="Field that allow to compute field and store them even if they are based on the current date", default=fields.Date.today)
    cooperator_id = fields.Many2one('res.partner')
    active = fields.Boolean(related="cooperator_id.active", store=True, index=True)
    info_session = fields.Boolean('Information Session ?')
    info_session_date = fields.Date('Information Session Date')
    super = fields.Boolean("Super Cooperative")
    sr = fields.Integer("Regular shifts counter", default=0)
    sc = fields.Integer("Compensation shifts counter", default=0)
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
                               ('exempted', 'Exempted'),
                               ('unsubscribed', 'Unsubscribed'),
                               ('resigning', 'Resigning')],
                              compute="_compute_status", string="Cooperative Status", store=True)
    can_shop = fields.Boolean(compute='_compute_status', store=True)
    history_ids = fields.One2many('cooperative.status.history', 'status_id', readonly=True)
    unsubscribed = fields.Boolean(default=False, help="Manually unsubscribed")
    resigning = fields.Boolean(default=False, help="Want to leave the beescoop")

    #Specific to irregular
    irregular_start_date = fields.Date()  #TODO migration script
    irregular_absence_date = fields.Date()
    irregular_absence_counter = fields.Integer() #TODO unsubscribe when reach -2
    future_alert_date = fields.Date(compute='_compute_future_alert_date')
    next_countdown_date = fields.Date(compute='_compute_next_countdown_date')

    temporary_exempt_reason_id = fields.Many2one('cooperative.exempt.reason', 'Exempt Reason')
    temporary_exempt_start_date = fields.Date()
    temporary_exempt_end_date = fields.Date()


    @api.depends('today', 'sr', 'sc', 'holiday_end_time',
                 'holiday_start_time', 'time_extension',
                 'alert_start_time', 'extension_start_time',
                 'unsubscribed', 'irregular_absence_date',
                 'irregular_absence_counter', 'temporary_exempt_start_date',
                 'temporary_exempt_end_date', 'resigning', 'cooperator_id.subscribed_shift_ids')
    def _compute_status(self):
        alert_delay = int(self.env['ir.config_parameter'].get_param('alert_delay', 28))
        grace_delay = int(self.env['ir.config_parameter'].get_param('default_grace_delay', 10))
        update = int(self.env['ir.config_parameter'].get_param('always_update', False))
        for rec in self:
            if update or not rec.today:
                rec.status = 'ok'
                rec.can_shop = True
                continue
            if rec.resigning:
                rec.status = 'resigning'
                rec.can_shop = False
                continue

            if rec.working_mode == 'regular':
                rec._set_regular_status(grace_delay, alert_delay)
            elif rec.working_mode == 'irregular':
                rec._set_irregular_status(grace_delay, alert_delay)
            elif rec.working_mode == 'exempt':
                rec.status = 'ok'
                rec.can_shop = True

    @api.depends('today', 'irregular_start_date', 'sr', 'holiday_start_time',
                 'holiday_end_time', 'temporary_exempt_start_date',
                 'temporary_exempt_end_date')
    def _compute_future_alert_date(self):
        """Compute date before which the worker is up to date"""
        for rec in self:
            # Only for irregular worker
            if rec.working_mode != 'irregular' and not rec.irregular_start_date:
                rec.future_alert_date = False
            # Alert start time already set
            elif rec.alert_start_time:
                rec.future_alert_date = False
            # Holidays are not set properly
            elif bool(rec.holiday_start_time) != bool(rec.holiday_end_time):
                rec.future_alert_date = False
            # Exemption have not a start and end time
            elif (bool(rec.temporary_exempt_start_date)
                  != bool(rec.temporary_exempt_end_date)):
                rec.future_alert_date = False
            else:
                date = rec.today
                counter = rec.sr
                # Simulate the countdown
                while counter > 0:
                    date = add_days_delta(date, 1)
                    date = self._next_countdown_date(rec.irregular_start_date,
                                                     date)
                    # Check holidays
                    if (rec.holiday_start_time and rec.holiday_end_time
                            and date >= rec.holiday_start_time
                            and date <= rec.holiday_end_time):
                        continue
                    # Check temporary exemption
                    elif (rec.temporary_exempt_start_date
                          and rec.temporary_exempt_end_date
                          and date >= rec.temporary_exempt_start_date
                          and date <= rec.temporary_exempt_end_date):
                        continue
                    else:
                        counter -= 1
                rec.future_alert_date = self._next_countdown_date(
                    rec.irregular_start_date, date
                )

    @api.depends('today', 'irregular_start_date', 'holiday_start_time',
                 'holiday_end_time', 'temporary_exempt_start_date',
                 'temporary_exempt_end_date')
    def _compute_next_countdown_date(self):
        """
        Compute the following countdown date. This date is the date when
        the worker will see his counter changed du to the cron. This
        date is like the birthday date of the worker that occurred each
        PERIOD.
        """
        for rec in self:
            # Only for irregular worker
            if rec.working_mode != 'irregular' and not rec.irregular_start_date:
                rec.next_countdown_date = False
            # Holidays are not set properly
            elif bool(rec.holiday_start_time) != bool(rec.holiday_end_time):
                rec.next_countdown_date = False
            # Exemption have not a start and end time
            elif (bool(rec.temporary_exempt_start_date)
                  != bool(rec.temporary_exempt_end_date)):
                rec.next_countdown_date = False
            else:
                date = rec.today
                next_countdown_date = False
                while not next_countdown_date:
                    date = self._next_countdown_date(rec.irregular_start_date, date)
                    # Check holidays
                    if (rec.holiday_start_time and rec.holiday_end_time
                            and date >= rec.holiday_start_time
                            and date <= rec.holiday_end_time):
                        date = add_days_delta(date, 1)
                        continue
                    # Check temporary exemption
                    elif (rec.temporary_exempt_start_date
                          and rec.temporary_exempt_end_date
                          and date >= rec.temporary_exempt_start_date
                          and date <= rec.temporary_exempt_end_date):
                        date = add_days_delta(date, 1)
                        continue
                    else:
                        next_countdown_date = date
                rec.next_countdown_date = next_countdown_date

    @api.constrains("working_mode", "irregular_start_date")
    def _constrains_irregular_start_date(self):
        if self.working_mode == "irregular" and not self.irregular_start_date:
            raise UserError(_("Irregular workers must have an irregular start date."))

    def _next_countdown_date(self, irregular_start_date, today=False):
        """
        Return the next countdown date given irregular_start_date and
        today dates.
        This does not take holiday and other status into account.
        """
        today = today or fields.Date.today()

        delta = (today - irregular_start_date).days
        if not delta % PERIOD:
            return today
        return add_days_delta(today, PERIOD - (delta % PERIOD))

    def _set_regular_status(self, grace_delay, alert_delay):
        self.ensure_one()
        counter_unsubscribe = int(self.env['ir.config_parameter'].get_param('regular_counter_to_unsubscribe', -4))
        ok = self.sr >= 0 and self.sc >= 0
        grace_delay = grace_delay + self.time_extension

        if (self.sr + self.sc) <= counter_unsubscribe or self.unsubscribed:
            self.status = 'unsubscribed'
            self.can_shop = False
        #Check if exempted. Exempt end date is not required.
        elif self.temporary_exempt_start_date and self.today >= self.temporary_exempt_start_date:
            if not self.temporary_exempt_end_date or self.today <= self.temporary_exempt_end_date:
                self.status = 'exempted'
                self.can_shop = True

        #Transition to alert sr < 0 or stay in alert sr < 0 or sc < 0 and thus alert time is defined
        elif not ok and self.alert_start_time and self.extension_start_time and self.today <= add_days_delta(self.extension_start_time, grace_delay):
            self.status = 'extension'
            self.can_shop = True
        elif not ok and self.alert_start_time and self.extension_start_time and self.today > add_days_delta(self.extension_start_time, grace_delay):
            self.status = 'suspended'
            self.can_shop = False
        elif not ok and self.alert_start_time and self.today > add_days_delta(self.alert_start_time, alert_delay):
            self.status = 'suspended'
            self.can_shop = False
        elif (self.sr < 0) or (not ok and self.alert_start_time):
            self.status = 'alert'
            self.can_shop = True

        #Check for holidays; Can be in holidays even in alert or other mode ?
        elif (
            self.holiday_start_time
            and self.holiday_end_time
            and self.today >= self.holiday_start_time
            and self.today <= self.holiday_end_time
        ):

            self.status = 'holiday'
            self.can_shop = False
        elif ok or (not self.alert_start_time and self.sr >= 0):
            self.status = 'ok'
            self.can_shop = True

    def _set_irregular_status(self, grace_delay, alert_delay):
        counter_unsubscribe = int(self.env['ir.config_parameter'].get_param('irregular_counter_to_unsubscribe', -3))
        self.ensure_one()
        ok = self.sr >= 0
        grace_delay = grace_delay + self.time_extension
        if self.sr <= counter_unsubscribe or self.unsubscribed:
            self.status = 'unsubscribed'
            self.can_shop = False
        #Check if exempted. Exempt end date is not required.
        elif self.temporary_exempt_start_date and self.today >= self.temporary_exempt_start_date:
            if not self.temporary_exempt_end_date or self.today <= self.temporary_exempt_end_date:
                self.status = 'exempted'
                self.can_shop = True
        #Transition to alert sr < 0 or stay in alert sr < 0 or sc < 0 and thus alert time is defined
        elif not ok and self.alert_start_time and self.extension_start_time and self.today <= add_days_delta(self.extension_start_time, grace_delay):
            self.status = 'extension'
            self.can_shop = True
        elif not ok and self.alert_start_time and self.extension_start_time and self.today > add_days_delta(self.extension_start_time, grace_delay):
            self.status = 'suspended'
            self.can_shop = False
        elif not ok and self.alert_start_time and self.today > add_days_delta(self.alert_start_time, alert_delay):
            self.status = 'suspended'
            self.can_shop = False
        elif (self.sr < 0) or (not ok and self.alert_start_time):
            self.status = 'alert'
            self.can_shop = True

        #Check for holidays; Can be in holidays even in alert or other mode ?
        elif (
            self.holiday_start_time
            and self.holiday_end_time
            and self.today >= self.holiday_start_time
            and self.today <= self.holiday_end_time
        ):
            self.status = 'holiday'
            self.can_shop = False
        elif ok or (not self.alert_start_time and self.sr >= 0):
            self.status = 'ok'
            self.can_shop = True

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

    def _state_change(self, new_state):
        self.ensure_one()
        if new_state == 'alert':
            self.write({'alert_start_time': self.today, 'extension_start_time': False, 'time_extension': 0})
        if new_state == 'ok':
            data = {'extension_start_time': False, 'time_extension': 0}
            data['alert_start_time'] = False
            self.write(data)
        if new_state == 'unsubscribed' or new_state == 'resigning':
            # Remove worker from task_templates
            self.cooperator_id.sudo().write(
                {'subscribed_shift_ids': [(5, 0, 0)]})
            # Remove worker from supercoop in task_templates
            task_tpls = self.env['beesdoo.shift.template'].search(
                [('super_coop_id', 'in', self.cooperator_id.user_ids.ids)]
            )
            task_tpls.write({'super_coop_id': False})
            # Remove worker for future tasks (remove also supercoop)
            self.env['beesdoo.shift.shift'].sudo().unsubscribe_from_today(
                [self.cooperator_id.id], now=fields.Datetime.now()
            )

    def _change_counter(self, data):
        self.sc += data.get('sc', 0)
        self.sr += data.get('sr', 0)
        self.irregular_absence_counter += data.get('irregular_absence_counter', 0)
        self.irregular_absence_date = data.get('irregular_absence_date', False)

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
                    rec._state_change(vals['status'])
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

    @api.model
    def _cron_compute_counter_irregular(self, today=False):
        today = today or fields.Date.today()
        journal = self.env['beesdoo.shift.journal'].search([('date', '=', today)])
        if not journal:
            journal = self.env['beesdoo.shift.journal'].create({'date': today})
        domain = ['&',
                                     '&',
                                        '&', ('status', '!=', 'unsubscribed'),
                                             ('working_mode', '=', 'irregular'),
                                        ('irregular_start_date', '!=', False),
                                     '|',
                                        '|', ('holiday_start_time', '=', False), ('holiday_end_time', '=', False),
                                        '|', ('holiday_start_time', '>', today), ('holiday_end_time', '<', today),
        ]
        irregular = self.search(domain)
        for status in irregular:
            if status.status == 'exempted':
                continue
            delta = (today - status.irregular_start_date).days
            if delta and delta % PERIOD == 0 and status not in journal.line_ids:
                if status.sr > 0:
                    status.sr -= 1
                elif status.alert_start_time:
                    status.sr -= 1
                else:
                    status.sr -= 2
                journal.line_ids |= status


class ShiftCronJournal(models.Model):
    _name = 'beesdoo.shift.journal'
    _order = 'date desc'
    _rec_name = 'date'

    date = fields.Date()
    line_ids = fields.Many2many('cooperative.status')

    _sql_constraints = [
        ('one_entry_per_day', 'unique (date)', _('You can only create one journal per day')),
    ]

    @api.multi
    def run(self):
        self.ensure_one()
        if not self.user_has_groups('beesdoo_shift.group_cooperative_admin'):
            raise ValidationError(_("You don't have the access to perform this action"))
        self.sudo().env['cooperative.status']._cron_compute_counter_irregular(today=self.date)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cooperative_status_ids = fields.One2many('cooperative.status', 'cooperator_id', readonly=True)
    super = fields.Boolean(related='cooperative_status_ids.super', string="Super Cooperative", readonly=True, store=True)
    info_session = fields.Boolean(related='cooperative_status_ids.info_session', string='Information Session ?', readonly=True, store=True)
    info_session_date = fields.Date(related='cooperative_status_ids.info_session_date', string='Information Session Date', readonly=True, store=True)
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

    @api.multi
    def temporary_exempt(self):
        return {
           'name': _('Temporary Exemption'),
           'type': 'ir.actions.act_window',
           'view_type': 'form',
           'view_mode': 'form',
           'res_model': 'beesdoo.shift.temporary_exemption',
           'target': 'new',
        }

    #TODO access right + vue on res.partner
    #TODO can_shop : Status can_shop ou extempted ou part C
