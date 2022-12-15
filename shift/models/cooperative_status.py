import logging
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


def add_days_delta(date_from, days_delta):
    if not date_from:
        return date_from
    next_date = date_from + timedelta(days=days_delta)
    return next_date


class ExemptReason(models.Model):
    _name = "cooperative.exempt.reason"
    _description = "cooperative.exempt.reason"

    name = fields.Char(required=True)


class HistoryStatus(models.Model):
    _name = "cooperative.status.history"
    _description = "cooperative.status.history"

    _order = "create_date desc"

    status_id = fields.Many2one("cooperative.status")
    cooperator_id = fields.Many2one("res.partner")
    change = fields.Char()
    type = fields.Selection(
        [("status", "Status Change"), ("counter", "Counter Change")]
    )
    user_id = fields.Many2one("res.users", string="User")


class CooperativeStatus(models.Model):
    _name = "cooperative.status"
    _description = "cooperative.status"
    _rec_name = "cooperator_id"
    _order = "cooperator_id"
    _period = 28

    def _get_status(self):
        # since the terms of these status are translated as "code" type
        # if they are already translated elsewhere, it won't be possible
        # to translate them to a specific status.
        # Hence these unique terms that have to be translated at module
        # configuration.
        return [
            ("ok", _("shift_status_up_to_date")),
            ("alert", _("shift_status_warning")),
            ("suspended", _("shift_status_suspended")),
            ("extension", _("shift_status_extension")),
            ("unsubscribed", _("shift_status_unsubscribed")),
            ("exempted", _("shift_status_exempted")),
            ("holiday", _("shift_status_holidays")),
            ("resigning", _("shift_status_resigning")),
        ]

    today = fields.Date(
        help="Field that allow to compute field and store them even if they "
        "are based on the current date",
        default=fields.Date.today,
    )
    cooperator_id = fields.Many2one("res.partner")  # todo rename to worker_id
    active = fields.Boolean(related="cooperator_id.active", store=True, index=True)
    info_session = fields.Boolean("Information Session ?")
    info_session_date = fields.Date("Information Session Date")
    super = fields.Boolean("Super Cooperative")
    sr = fields.Integer("Regular shifts counter", default=0)
    sc = fields.Integer("Compensation shifts counter", default=0)
    time_extension = fields.Integer(
        "Extension Days NB",
        default=0,
        help="Addtional days to the automatic extension, 5 mean that you have "
        "a total of 15 extension days of default one is set to 10",
    )
    holiday_start_time = fields.Date("Holidays Start Day")
    holiday_end_time = fields.Date("Holidays End Day")
    alert_start_time = fields.Date("Alert Start Day")
    extension_start_time = fields.Date("Extension Start Day")
    working_mode = fields.Selection(
        [
            ("regular", "Regular worker"),
            ("irregular", "Irregular worker"),
            ("exempt", "Exempted"),
        ],
        string="Working mode",
    )
    exempt_reason_id = fields.Many2one(
        comodel_name="cooperative.exempt.reason", string="Exempt Reason"
    )
    status = fields.Selection(
        selection=lambda x: x._get_status(),
        compute="_compute_status",
        string="Cooperative Status",
        translate=True,
        store=True,
    )
    can_shop = fields.Boolean(compute="_compute_can_shop", store=True)
    history_ids = fields.One2many(
        "cooperative.status.history", "status_id", readonly=True
    )
    unsubscribed = fields.Boolean(default=False, help="Manually unsubscribed")
    resigning = fields.Boolean(default=False, help="Want to leave the beescoop")

    # Specific to irregular
    irregular_start_date = fields.Date()  # TODO migration script
    irregular_absence_date = fields.Date()
    irregular_absence_counter = fields.Integer()  # TODO unsubscribe when reach -2
    future_alert_date = fields.Date(compute="_compute_future_alert_date")
    next_countdown_date = fields.Date(compute="_compute_next_countdown_date")
    next_shift_id = fields.Many2one(
        comodel_name="beesdoo.shift.shift",
        string="Earliest Open Shift",
        compute="_compute_next_shift",
        store=True,
        help="Earliest open shift the worker is subscribed to.",
    )
    next_shift_date = fields.Datetime(
        related="next_shift_id.start_time",
        string="Next Shift Date",
        store=True,
    )
    is_subscribed_to_shift = fields.Boolean(
        string="Subscribed before Alert Date",
        compute="_compute_next_shift",
        store=True,
    )
    temporary_exempt_reason_id = fields.Many2one(
        comodel_name="cooperative.exempt.reason",
        string="Temporary Exempt Reason",
    )
    temporary_exempt_start_date = fields.Date()
    temporary_exempt_end_date = fields.Date()

    @api.depends("status")
    def _compute_can_shop(self):
        for rec in self:
            rec.can_shop = rec.status in self._can_shop_status()

    @api.depends(
        "today",
        "sr",
        "sc",
        "holiday_end_time",
        "holiday_start_time",
        "time_extension",
        "alert_start_time",
        "extension_start_time",
        "unsubscribed",
        "irregular_absence_date",
        "irregular_absence_counter",
        "temporary_exempt_start_date",
        "temporary_exempt_end_date",
        "resigning",
        "cooperator_id.subscribed_shift_ids",
        "working_mode",
    )
    def _compute_status(self):
        update = int(
            self.env["ir.config_parameter"].sudo().get_param("always_update", False)
        )
        for rec in self:
            if update or not rec.today:
                rec.status = "ok"
                continue
            if rec.resigning:
                rec.status = "resigning"
                continue

            if rec.working_mode == "regular":
                rec.status = rec._get_regular_status()
            elif rec.working_mode == "irregular":
                rec.status = rec._get_irregular_status()
            elif rec.working_mode == "exempt":
                rec.status = "ok"

    _sql_constraints = [
        (
            "cooperator_uniq",
            "unique (cooperator_id)",
            _("You can only set one cooperator status per cooperator"),
        )
    ]

    @api.constrains("working_mode", "irregular_start_date")
    def _constrains_irregular_start_date(self):
        if self.working_mode == "irregular" and not self.irregular_start_date:
            raise UserError(_("Irregular workers must have an irregular start date."))

    def _get_watched_fields(self):
        """
        Make the list of field use
        to trigger history tracking configurable
        """
        return [
            "sr",
            "sc",
            "time_extension",
            "extension_start_time",
            "alert_start_time",
            "unsubscribed",
        ]

    @api.multi
    def write(self, vals):
        """
        Overwrite write to historize the change
        """
        for field in self._get_watched_fields():
            if field not in vals:
                continue
            for rec in self:
                data = {
                    "status_id": rec.id,
                    "cooperator_id": rec.cooperator_id.id,
                    "type": "counter",
                    "user_id": self.env.context.get("real_uid", self.env.uid),
                }
                if vals.get(field, rec[field]) != rec[field]:
                    data["change"] = "{}: {} -> {}".format(
                        field.upper(), rec[field], vals.get(field)
                    )
                    self.env["cooperative.status.history"].sudo().create(data)
        previous_vals = {}
        for rec in self:
            previous_vals[rec] = {
                "holiday_start_time": rec.holiday_start_time,
                "holiday_end_time": rec.holiday_end_time,
                "temporary_exempt_start_date": rec.temporary_exempt_start_date,
                "temporary_exempt_end_date": rec.temporary_exempt_end_date,
            }
        result = super(CooperativeStatus, self).write(vals)
        if "holiday_start_time" in vals or "holiday_end_time" in vals:
            for rec in self:
                rec._update_shifts_based_on_dates(
                    prev_start_date=previous_vals[rec]["holiday_start_time"],
                    prev_end_date=previous_vals[rec]["holiday_end_time"],
                    cur_start_date=self.holiday_start_time,
                    cur_end_date=self.holiday_end_time,
                )
        if "temporary_exempt_start_date" in vals or "temporary_exempt_end_date" in vals:
            for rec in self:
                rec._update_shifts_based_on_dates(
                    prev_start_date=previous_vals[rec]["temporary_exempt_start_date"],
                    prev_end_date=previous_vals[rec]["temporary_exempt_end_date"],
                    cur_start_date=self.temporary_exempt_start_date,
                    cur_end_date=self.temporary_exempt_end_date,
                )
        return result

    @api.multi
    def _write(self, vals):
        """
        Overwrite write to historize the change of status
        and make action on status change
        """
        if "status" in vals:
            self._cr.execute(
                'select id, status, sr, sc from "%s" where id in %%s' % self._table,
                (self._ids,),
            )
            result = self._cr.dictfetchall()
            old_status_per_id = {r["id"]: r for r in result}
            for rec in self:
                if old_status_per_id[rec.id]["status"] != vals["status"]:
                    data = {
                        "status_id": rec.id,
                        "cooperator_id": rec.cooperator_id.id,
                        "type": "status",
                        "change": "STATUS: %s -> %s"
                        % (
                            old_status_per_id[rec.id]["status"],
                            vals["status"],
                        ),
                        "user_id": self.env.context.get("real_uid", self.env.uid),
                    }
                    self.env["cooperative.status.history"].sudo().create(data)
                    rec._state_change(vals["status"])
        return super(CooperativeStatus, self)._write(vals)

    def _update_shifts_based_on_dates(
        self, prev_start_date, prev_end_date, cur_start_date, cur_end_date
    ):
        """
        Update already generated shifts according to previous start and
        end date and to futur start and end date given in args.

        Shift in the past will not be changed !
        """
        self.ensure_one()
        today = self.today or fields.Date.today()
        self.env["beesdoo.shift.shift"].unsubscribe_from_today(
            worker_ids=self.cooperator_id,
            task_tmpl_ids=self.cooperator_id.subscribed_shift_ids,
            today=cur_start_date if cur_start_date >= today else today,
            end_date=cur_end_date,
        )
        # If the previous holidays are in the future and that holiday
        # period changes, worker needs to be subscribed again to shifts
        if (
            prev_start_date
            and prev_start_date > today
            and cur_start_date > prev_start_date
        ):
            # subscribe worker from prev to current start_time
            self.env["beesdoo.shift.shift"].subscribe_from_today(
                worker_ids=self.cooperator_id,
                task_tmpl_ids=self.cooperator_id.subscribed_shift_ids,
                today=prev_start_date,
                end_date=cur_start_date - timedelta(days=1),
            )
        if prev_end_date and prev_end_date > today and cur_end_date < prev_end_date:
            # subscribe worker from current to prev end time
            self.env["beesdoo.shift.shift"].subscribe_from_today(
                worker_ids=self.cooperator_id,
                task_tmpl_ids=self.cooperator_id.subscribed_shift_ids,
                today=cur_end_date + timedelta(days=1),
                end_date=prev_end_date,
            )

    def get_status_value(self):
        """
        Workaround to get translated selection value instead of key in mail
        template.
        """
        state_list = (
            self.env["cooperative.status"]
            ._fields["status"]
            ._description_selection(self.env)
        )
        return dict(state_list)[self.status]

    @api.model
    def _set_today(self):
        """
        Method call by the cron to update store value base on the date
        """
        self.search([]).write({"today": fields.Date.today()})

    @api.model
    def _cron_compute_counter_irregular(self, today=False):
        """
        Journal ensure that a irregular worker will be only check
        once per day
        """
        today = today or fields.Date.today()
        journal = self.env["beesdoo.shift.journal"].search([("date", "=", today)])
        if not journal:
            journal = self.env["beesdoo.shift.journal"].create({"date": today})

        domain = self._get_irregular_worker_domain(today)
        irregular = self.search(domain)
        for status in irregular:
            delta = (today - status.irregular_start_date).days
            if delta and delta % self._period == 0 and status not in journal.line_ids:
                status._change_irregular_counter()
                journal.line_ids |= status

    @api.multi
    def clear_history(self):
        self.ensure_one()
        self.history_ids.unlink()

    ########################################################
    #                   Method to override                 #
    #           To define the behavior of the status       #
    #                                                      #
    #       By default: everyone is always up to date      #
    ########################################################

    ##############################
    #   Computed field section   #
    ##############################
    @api.depends("today")
    def _compute_future_alert_date(self):
        """
        Compute date until the worker is up to date
        for irregular worker
        """
        for rec in self:
            rec.future_alert_date = False

    @api.depends("today")
    def _compute_next_countdown_date(self):
        """
        Compute the following countdown date. This date is the date when
        the worker will see his counter changed due to the cron. This
        date is like the birthday date of the worker that occurred each
        _period.
        """
        for rec in self:
            rec.next_countdown_date = False

    @api.multi
    @api.depends(
        "cooperator_id.shift_shift_ids",
        "cooperator_id.shift_shift_ids.state",
        "future_alert_date",
        "today",
    )
    def _compute_next_shift(self):
        # avoid searching for shift in loop
        cooperator_ids = self.mapped("cooperator_id").ids
        # rather take earliest "open" (confirmed) shift
        # in order to take into account partners for which
        # the counter was not incremented (happens when passing to "done")
        next_shifts = self.env["beesdoo.shift.shift"].search(
            [("state", "=", "open"), ("worker_id", "in", cooperator_ids)],
            order="worker_id, start_time",
        )

        next_shift_by_worker = {}
        for shift in next_shifts:
            #  take first shift for each worker
            next_shift_by_worker.setdefault(shift.worker_id.id, shift)

        # what happens when no future shift ?
        for rec in self:
            rec.next_shift_id = next_shift_by_worker.get(rec.cooperator_id.id)

            if not rec.next_shift_id:
                rec.is_subscribed_to_shift = False
                continue

            if not rec.future_alert_date:
                rec.is_subscribed_to_shift = True
                continue

            future_alert_date_time = datetime(
                rec.future_alert_date.year,
                rec.future_alert_date.month,
                rec.future_alert_date.day,
            )
            rec.is_subscribed_to_shift = (
                rec.next_shift_id.start_time < future_alert_date_time
            )

    def _can_shop_status(self):
        """
        return the list of status that give access
        to active cooperator privilege
        """
        return ["ok", "alert", "extension", "exempted"]

    #####################################
    #   Status Change implementation    #
    #####################################

    def _get_regular_status(self):
        """
        Return the value of the status
        for the regular worker
        """
        return "ok"

    def _get_irregular_status(self):
        """
        Return the value of the status
        for the irregular worker
        """
        return "ok"

    def _state_change(self, new_state):
        """
        Hook to watch change in the state
        """

    def _change_counter(self, data):
        """
        Call when a shift state is changed
        use data generated by _get_counter_date_state_change
        """

    ###############################################
    #        Irregular Cron implementation        #
    ###############################################

    def _get_irregular_worker_domain(self, today):
        """
        return the domain the give the list
        of valid irregular worker that should
        get their counter changed by the cron
        """
        return [(0, "=", 1)]

    def _change_irregular_counter(self):
        """
        Define how the counter will change
        for the irregular worker
        where today - start_date is a multiple of the period
        by default 28 days
        """


class ShiftCronJournal(models.Model):
    _name = "beesdoo.shift.journal"
    _description = "beesdoo.shift.journal"
    _order = "date desc"
    _rec_name = "date"

    date = fields.Date()
    line_ids = fields.Many2many("cooperative.status")

    _sql_constraints = [
        (
            "one_entry_per_day",
            "unique (date)",
            _("You can only create one journal per day"),
        )
    ]

    @api.multi
    def run(self):
        self.ensure_one()
        if not self.user_has_groups("beesdoo_shift.group_cooperative_admin"):
            raise ValidationError(_("You don't have the access to perform this action"))
        self.sudo().env["cooperative.status"]._cron_compute_counter_irregular(
            today=self.date
        )
