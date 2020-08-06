from datetime import datetime

from odoo import api, models, fields
from odoo.addons.beesdoo_shift.models.cooperative_status import add_days_delta

class TaskType(models.Model):
    _inherit = "beesdoo.shift.type"

    super_only = fields.Boolean('Referent Only')

class TaskTemplate(models.Model):
    _inherit = 'beesdoo.shift.template'

    super_only = fields.Boolean(related="task_type_id.super_only")
    shift_presence_value = fields.Float(default=1.0)

class WizardSubscribe(models.TransientModel):
    _inherit = 'beesdoo.shift.subscribe'

    def _get_mode(self):
        partner = self.env["res.partner"].browse(self._context.get("active_id"))
        return partner.working_mode or 'irregular'

    working_mode = fields.Selection(selection=[
            ("irregular", "worker"),
            ("exempt", "Exempted"),
        ], default=_get_mode)

class Task(models.Model):
    _inherit = 'beesdoo.shift.shift'

    can_unsubscribe = fields.Boolean(compute="_compute_can_unsubscribe")
    super_only = fields.Boolean(related="task_type_id.super_only")

    def _get_selection_status(self):
        return [
            ("open","Confirmed"),
            ("done","Attended"),
            ("absent","Absent"),
            ("cancel","Cancelled")
        ]

    def _get_counter_date_state_change(self, new_state):
        """
        Return the cooperator_status of the cooperator that need to be
        change and data that need to be change. It does not perform the
        change directly. The cooperator_status will be changed by the
        _change_counter function.

        Check has been done to ensure that worker is legitimate.
        """
        data = {}
        status = self.worker_id.cooperative_status_ids[0]
        if new_state == "done":
            data['sr'] = self.task_template_id.shift_presence_value or 1.0

        return data, status

    def _compute_can_unsubscribe(self):
        now = datetime.now()
        ICP = self.env["ir.config_parameter"].sudo()
        max_hours = int(ICP.get_param("max_hours_to_unsubscribe", 2))
        for rec in self:
            if now > rec.start_time or rec.state != 'open':
                rec.can_unsubscribe = False
            else:
                delta = (now - rec.start_time).seconds / 3600.0
                rec.can_unsubscribe = delta >= max_hours


    def write(self, vals):
        if 'worker_id' in vals:
            template_unsubscribed = self.env.ref("macavrac_base.email_template_shift_unsubscribed") 
            template_subscribed = self.env.ref("macavrac_base.email_template_shift_subscribed")
            new_worker_id = self.env['beesdoo.shift.shift'].browse(vals.get('worker_id'))
            for record in self:
                old_worker_id  = record.worker_id
                if old_worker_id:
                    template_unsubscribed.send_mail(record.id)
                if new_worker_id and old_worker_id != new_worker_id:
                    res = super(Task, record).write(vals)
                    template_subscribed.send_mail(record.id)
        return super(Task, self).write(vals)


class CooperativeStatus(models.Model):
    _inherit = 'cooperative.status'

    def _get_status(self):
        return [
            ("ok", "Up to Date"),
            ("alert", "Alerte"),
            ("suspended", "Suspended"),
            ("exempted", "Exempted"),
            ("unsubscribed", "Unsubscribed"),
            ("resigning", "Resigning"),
        ]
    # TODO auto init for automatic migration 
    sr = fields.Float()
    future_alert_date = fields.Date(compute="_compute_future_alert_date")
    next_countdown_date = fields.Date(compute="_compute_next_countdown_date")

    ########################################################
    #                   Method to override                 #
    #           To define the behavior of the status       #
    #                                                      #
    #       By default: everyone is always up to date      #
    ########################################################

    ##############################
    #   Computed field section   #
    ##############################
    def _next_countdown_date(self, irregular_start_date, today):
        """
        Return the next countdown date given irregular_start_date and
        today dates.
        This does not take holiday and other status into account.
        """

        delta = (today - irregular_start_date).days
        if not delta % self._period:
            return today
        return add_days_delta(today, self._period - (delta % self._period))


    @api.depends(
        "today",
        "sr",
        "temporary_exempt_start_date",
        "temporary_exempt_end_date",
    )
    def _compute_future_alert_date(self):
        """Compute date before which the worker is up to date"""
        for rec in self:
            # Only for irregular worker
            # Alert start time already set
            real_today = rec.today
            if rec.alert_start_time:
                rec.future_alert_date = False
            elif rec.working_mode != "irregular" or not rec.irregular_start_date:
                rec.future_alert_date = False
            else:
                date = rec.today
                counter = rec.sr
                next_countdown_date = False
                while counter >= 0:
                    next_countdown_date = self._next_countdown_date(rec.irregular_start_date, date)
                    rec.today = next_countdown_date
                    if rec.status != 'exempted':
                        counter -= 1
                        rec.today = real_today
                    date = add_days_delta(next_countdown_date, 1)
                rec.future_alert_date = next_countdown_date
                rec.today = real_today

    
    @api.depends(
        "today",
        "irregular_start_date",
        "holiday_start_time",
        "holiday_end_time",
        "temporary_exempt_start_date",
        "temporary_exempt_end_date",
    )
    def _compute_next_countdown_date(self):
        """
        Compute the following countdown date. This date is the date when
        the worker will see his counter changed du to the cron. This
        date is like the birthday date of the worker that occurred each
        PERIOD.
        """
        for rec in self:
            real_today = rec.today
            # Only for irregular worker
            if rec.working_mode != "irregular" or not rec.irregular_start_date:
                rec.next_countdown_date = False
            else:
                next_countdown_date = rec.today
                while True:
                    next_countdown_date = self._next_countdown_date(rec.irregular_start_date, next_countdown_date)
                    rec.today = next_countdown_date
                    if rec.status != 'exempted':
                        rec.next_countdown_date = next_countdown_date
                        rec.today = real_today
                        break
                    else:
                        next_countdown_date = add_days_delta(next_countdown_date, 1)

    #####################################
    #   Status Change implementation    #
    #####################################

    def _get_regular_status(self):
        """
            Return the value of the status
            for the regular worker
        """
        ICP = self.env["ir.config_parameter"].sudo()
        suspended_count = int(ICP.get_param("suspended_count", -2))
        unsubscribed_count = int(ICP.get_param("unsubscribed_count", -4))
        if (self.temporary_exempt_start_date 
            and self.temporary_exempt_end_date 
            and self.today >= self.temporary_exempt_start_date 
            and self.today <= self.temporary_exempt_end_date
        ):
            return 'exempted'
        if self.sr >= 0:
            return 'ok'

        if self.sr <= unsubscribed_count:
            return 'unsubscribed'
        if self.sr <= suspended_count:
            return 'suspended'
        if self.sr < 0:
            return 'alert'
        return 'ok'

    def _get_irregular_status(self):
        """
            Return the value of the status
            for the irregular worker
        """
        return self._get_regular_status()

    def _state_change(self, new_state):
        """
            Hook to watch change in the state
        """
        self.ensure_one()
        if new_state == "unsubscribed" or new_state == "resigning":
            # Remove worker from task_templates
            self.cooperator_id.sudo().write(
                {"subscribed_shift_ids": [(5, 0, 0)]}
            )
            # Remove worker from supercoop in task_templates
            task_tpls = self.env["beesdoo.shift.template"].search(
                [("super_coop_id", "in", self.cooperator_id.user_ids.ids)]
            )
            task_tpls.write({"super_coop_id": False})
            # Remove worker for future tasks (remove also supercoop)
            self.env["beesdoo.shift.shift"].sudo().unsubscribe_from_today(
                [self.cooperator_id.id], now=fields.Datetime.now()
            )
        if new_state == "alert":
            self.write({"alert_start_time": self.today})

    def _change_counter(self, data):
        """
            Call when a shift state is changed
            use data generated by _get_counter_date_state_change
        """
        self.sr += data.get("sr", 0)


    ###############################################
    ###### Irregular Cron implementation ##########
    ###############################################

    def _get_irregular_worker_domain(self, today):
        """
            return the domain the give the list
            of valid irregular worker that should
            get their counter changed by the cron
        """
        return [
            ("status", "not in", ["unsubscribed", "exempted", "resigning"]),
            ("irregular_start_date", "!=", False),
        ]

    def _change_irregular_counter(self):
        """
            Define how the counter will change
            for the irregular worker
            where today - start_date is a multiple of the period
            by default 28 days
        """
        self.sr -= 1

