import itertools
import json
from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Task(models.Model):
    _name = "beesdoo.shift.shift"
    _inherit = ["mail.thread"]
    _order = "start_time asc"

    ##################################
    # Method to override             #
    # to have different state        #
    # on the shift                   #
    ##################################
    def _get_selection_status(self):
        return [
            ("open", _("Confirmed")),
            ("done", _("Attended")),
            ("absent", _("Absent")),
            ("excused", _("Excused")),
            ("cancel", _("Cancelled")),
        ]

    def _get_color_mapping(self, state):
        return {
            "draft": 0,
            "open": 1,
            "done": 5,
            "absent": 2,
            "excused": 3,
            "cancel": 9,
        }[state]

    def _get_final_state(self):
        return ["done", "absent", "excused"]

    name = fields.Char(track_visibility="always")
    task_template_id = fields.Many2one("beesdoo.shift.template")
    planning_id = fields.Many2one(related="task_template_id.planning_id", store=True)
    task_type_id = fields.Many2one("beesdoo.shift.type", string="Task Type")
    worker_id = fields.Many2one(
        "res.partner",
        track_visibility="onchange",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )
    start_time = fields.Datetime(track_visibility="always", index=True, required=True)
    end_time = fields.Datetime(track_visibility="always", required=True)
    state = fields.Selection(
        selection=lambda x: x._get_selection_status(),
        default="open",
        required=True,
        track_visibility="onchange",
        group_expand="_expand_states",
    )
    color = fields.Integer(compute="_compute_color")
    super_coop_id = fields.Many2one(
        "res.users",
        string="Super Cooperative",
        domain=[("partner_id.super", "=", True)],
        track_visibility="onchange",
    )
    is_regular = fields.Boolean(default=False, string="Regular shift")
    is_compensation = fields.Boolean(default=False, string="Compensation shift")
    replaced_id = fields.Many2one(
        "res.partner",
        track_visibility="onchange",
        domain=[
            ("eater", "=", "worker_eater"),
            ("working_mode", "=", "regular"),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )
    revert_info = fields.Text(copy=False)
    working_mode = fields.Selection(related="worker_id.working_mode")

    def _expand_states(self, states, domain, order):
        return [key for key, val in self._fields["state"].selection(self)]

    @api.depends("state")
    def _compute_color(self):
        for rec in self:
            rec.color = self._get_color_mapping(rec.state)

    @api.constrains("state")
    def _lock_future_task(self):
        if datetime.now() < self.start_time:
            if self.state in self._get_final_state():
                raise UserError(
                    _(
                        "Shift state of a future shift "
                        "can't be set to 'present' or 'absent'."
                    )
                )

    def message_auto_subscribe(self, updated_fields, values=None):
        self._add_follower(values)
        return super(Task, self).message_auto_subscribe(updated_fields, values=values)

    def _add_follower(self, vals):
        if vals.get("worker_id"):
            worker = self.env["res.partner"].browse(vals["worker_id"])
            self.message_subscribe(partner_ids=worker.ids)

    # TODO button to replace someone
    @api.model
    def unsubscribe_from_today(
        self,
        worker_ids,
        task_tmpl_ids=None,
        today=None,
        end_date=None,
        now=None,
    ):
        """
        Unsubscribe workers from *worker_ids* from all shift that start
          *today* and later. If *task_tmpl_ids* is set, unsubscribe
          *worker_ids* only from shift related to *task_tmpl_ids*.

        If *end_date* is given, unsubscribe workers from shift between *today*
          and *end_date*.
        If *now* is given workers are unsubscribed from all shifts starting
           *now* and later.

        :type today: date
        :type end_date: date
        :type now: datetime
        """
        if not worker_ids:
            return
        if now:
            if not isinstance(now, datetime):
                raise UserError(_("'Now' must be a datetime."))
            date_domain = [("start_time", ">", now)]
        else:
            today = today or fields.Date.today()
            today = datetime.combine(today, time())
            date_domain = [("start_time", ">=", today)]
        if end_date:
            end_date = datetime.combine(end_date, time(hour=23, minute=59, second=59))
            date_domain.append(("end_time", "<=", end_date))

        domain = [("worker_id", "in", worker_ids.ids)]
        if task_tmpl_ids:
            domain += [("task_template_id", "in", task_tmpl_ids.ids)]

        to_unsubscribe = self.search(domain + date_domain)
        to_unsubscribe.write({"worker_id": False})

        # Remove worker, replaced_id and regular
        to_unsubscribe_replace = self.search(
            [("replaced_id", "in", worker_ids.ids)] + date_domain
        )
        to_unsubscribe_replace.write({"worker_id": False, "replaced_id": False})

        # If worker is Super cooperator, remove it from planning
        super_coop_ids = self.env["res.users"].search(
            [("partner_id", "in", worker_ids.ids), ("super", "=", True)]
        )

        if super_coop_ids:
            to_unsubscribe_super_coop = self.search(
                [("super_coop_id", "in", super_coop_ids.ids)] + date_domain
            )
            to_unsubscribe_super_coop.write({"super_coop_id": False})

    @api.model
    def subscribe_from_today(
        self,
        worker_ids,
        task_tmpl_ids,
        today=None,
        end_date=None,
        now=None,
    ):
        """
        Subscribe workers from *worker_ids* to a shift related to
        *task_tmpl_ids* starting from *today* or *now*, and ending to
        *end_date* (included) if specified.

        :type worker_ids: res.partner
        :type task_tmpl_ids: beesdoo.shift.template
        :type today: date
        :type end_date: date
        :type now: datetime
        """
        if not worker_ids:
            return
        if now:
            if not isinstance(now, datetime):
                raise UserError(_("'Now' must be a datetime."))
            date_domain = [("start_time", ">", now)]
        else:
            today = today or fields.Date.today()
            today = datetime.combine(today, time())
            date_domain = [("start_time", ">", today)]
        if end_date:
            end_date = datetime.combine(end_date, time(hour=23, minute=59, second=59))
            date_domain.append(("end_time", "<=", end_date))

        for task_tmpl_id in task_tmpl_ids:
            domain = [
                ("task_template_id", "=", task_tmpl_id.id),
                ("state", "=", "open"),
            ]
            shift_ids = self.env["beesdoo.shift.shift"].search(
                domain + date_domain, order="start_time"
            )
            # worker subscription
            for _key, shifts in itertools.groupby(
                shift_ids, lambda r: (r.start_time, r.end_time)
            ):
                shifts = list(shifts)  # shifts will be used several times
                empty_shifts = [shift for shift in shifts if not shift.worker_id]
                workers_not_already_subscribed = [
                    worker_id
                    for worker_id in worker_ids
                    if worker_id
                    not in (shift.worker_id for shift in shifts if shift.worker_id)
                ]
                for i, worker_id in enumerate(workers_not_already_subscribed):
                    if i < len(empty_shifts):
                        empty_shifts[i].write(
                            {"is_regular": True, "worker_id": worker_id.id}
                        )
                    else:
                        # TODO: it will be better to have a function
                        # that generate a new shift with default
                        # values and proper name instead of copying
                        # a existing shift that may have modified
                        # default values.
                        shifts[0].copy(
                            default={"is_regular": True}
                        ).worker_id = worker_id
            # Super coop subscription
            for worker_id in worker_ids:
                if task_tmpl_id.super_coop_id == worker_id:
                    shift_ids.write({"super_coop_id": worker_id})

    @api.multi
    def write(self, vals):
        """
        Overwrite write to track state change
        If worker is changer:
           Revert for the current worker
           Change the worker info
           Compute state change for the new worker
        """
        if "worker_id" in vals:
            for rec in self:
                if rec.worker_id.id != vals["worker_id"]:
                    rec._revert()
                    # To satisfy the constrains on worker_id, it must be
                    # accompanied by the change in is_regular and
                    # is_compensation field.
                    super(Task, rec).write(
                        {
                            "worker_id": vals["worker_id"],
                            "is_regular": vals.get("is_regular", rec.is_regular),
                            "is_compensation": vals.get(
                                "is_compensation", rec.is_compensation
                            ),
                        }
                    )
                    rec._update_state(rec.state)
        if "state" in vals:
            for rec in self:
                if vals["state"] != rec.state:
                    rec._update_state(vals["state"])
        return super(Task, self).write(vals)

    def _set_revert_info(self, data, status):
        data_new = {
            "status_id": status.id,
            "data": {
                k: data.get(k, 0) * -1
                for k in ["sr", "sc", "irregular_absence_counter"]
            },
        }
        if data.get("irregular_absence_date"):
            data_new["data"]["irregular_absence_date"] = False

        self.write({"revert_info": json.dumps(data_new)})

    def _revert(self):
        if not self.revert_info:
            return
        data = json.loads(self.revert_info)
        self.env["cooperative.status"].browse(data["status_id"]).sudo()._change_counter(
            data["data"]
        )
        self.revert_info = False

    def _update_state(self, new_state):
        self.ensure_one()
        self._revert()

        if (
            not (self.worker_id or self.replaced_id)
            and new_state in self._get_final_state()
        ):
            raise UserError(
                _(
                    "You cannot change to the status %s if no worker is "
                    "defined for the shift "
                )
                % new_state
            )

        always_update = int(
            self.env["ir.config_parameter"].sudo().get_param("always_update", False)
        )
        if always_update or not (self.worker_id or self.replaced_id):
            return

        if not (self.worker_id.working_mode in ["regular", "irregular"]):
            raise UserError(
                _(
                    "Working mode is not properly defined. Please check if "
                    "the worker is subscribed "
                )
            )

        data, status = self._get_counter_date_state_change(new_state)
        if status:
            status.sudo()._change_counter(data)
            self._set_revert_info(data, status)

    @api.model
    def _cron_send_weekly_emails(self, notice=1, period=7):
        """
        Send a summary email for all workers
        if they have a shift planned between `notice` and `notice + period` days.
        """
        tasks = self.env["beesdoo.shift.shift"]
        shift_summary_mail_template = self.env.ref(
            "beesdoo_shift.email_template_shift_summary", False
        )

        start_time = datetime.now() + timedelta(days=notice)
        end_time = datetime.now() + timedelta(days=notice + period)

        confirmed_tasks = tasks.search(
            [
                ("start_time", ">", start_time),
                ("start_time", "<", end_time),
                ("worker_id", "!=", False),
                ("state", "=", "open"),
            ]
        )

        for rec in confirmed_tasks:
            shift_summary_mail_template.send_mail(rec.id, True)

    ########################################################
    #                   Method to override                 #
    #           To define the behavior of the status       #
    #                                                      #
    #       By default: everyone is always up to date      #
    ########################################################

    def _get_counter_date_state_change(self, new_state):
        """
        Return the cooperator_status of the cooperator that need to be
        change and data that need to be change. It does not perform the
        change directly. The cooperator_status will be changed by the
        _change_counter function.

        Check has been done to ensure that worker is legitimate.
        """
        data = {}
        status = None
        return data, status
