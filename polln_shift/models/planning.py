# Copyright 2021 Coop IT Easy SCRL fs
#   Thibault François
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models

from odoo.addons.beesdoo_shift.models.cooperative_status import add_days_delta


def time_to_float(t):
    hour, minute = t.split(":")
    return float(hour) + float(minute) / 60


class WizardSubscribe(models.TransientModel):
    _inherit = "beesdoo.shift.subscribe"

    def _get_mode(self):
        partner = self.env["res.partner"].browse(self._context.get("active_id"))
        return partner.working_mode or "irregular"

    working_mode = fields.Selection(
        selection=[("irregular", "worker"), ("exempt", "Exempted")],
        default=_get_mode,
    )

    def subscribe(self):
        res = super().subscribe()
        if self.shift_id:
            # Write the shift whatever the mode is
            self.cooperator_id.sudo().write(
                {"subscribed_shift_ids": [(6, 0, [self.shift_id.id])]}
            )

        # Should work with module beesdoo_easy_my_coop but don't
        self.cooperator_id.eater = "worker_eater"
        return res


class Task(models.Model):
    _inherit = "beesdoo.shift.shift"

    _period = 28

    def _get_selection_status(self):
        return [
            ("open", _("Confirmed")),
            ("done", _("Attended (+1)")),
            ("absent", _("Absent (-1)")),
            ("excused", _("Excused (+0)")),
            ("cancel", _("Cancelled")),
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
            data["sr"] = 1.0
        if new_state == "absent":
            data["sr"] = -1.0
        return data, status

    def _get_final_state(self):
        """Disable constrains on shift that cannot be changed"""
        return []


class CooperativeStatus(models.Model):
    _inherit = "cooperative.status"

    def _get_status(self):
        return [
            ("ok", _("Up to Date")),
            ("alert", _("Alerte")),
            ("suspended", _("Suspended")),
            ("unsubscribed", _("Unsubscribed")),
            ("holiday", _("shift_status_holidays")),
            ("exempted", _("Exempted")),
            ("resigning", _("Resigning")),
        ]

    sr = fields.Float(compute="_compute_sr", inverse="_inverse_sr")
    # alter table cooperative_status add column sr_store double precision;
    # update cooperative_status set sr_store = sr;
    sr_store = fields.Float()
    future_alert_date = fields.Date(compute="_compute_future_alert_date")
    next_countdown_date = fields.Date(compute="_compute_next_countdown_date")

    def _compute_sr(self):
        for record in self:
            record.sr = record.sr_store

    def _inverse_sr(self):
        for record in self:
            record.sr_store = record.sr

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
        "irregular_start_date",
        "sr",
        "holiday_start_time",
        "holiday_end_time",
        "temporary_exempt_start_date",
        "temporary_exempt_end_date",
    )
    def _compute_future_alert_date(self):
        """Compute date before which the worker is up to date"""
        for rec in self:
            # Only for subscribed irregular worker
            if rec.working_mode != "irregular" or not rec.irregular_start_date:
                rec.future_alert_date = False
            # Alert start time already set
            elif rec.alert_start_time:
                rec.future_alert_date = False
            # Holidays are not set properly
            elif bool(rec.holiday_start_time) != bool(rec.holiday_end_time):
                rec.future_alert_date = False
            # Exemption have not a start and end time
            elif bool(rec.temporary_exempt_start_date) != bool(
                rec.temporary_exempt_end_date
            ):
                rec.future_alert_date = False
            else:
                date = rec.today
                counter = rec.sr
                # Simulate the countdown
                while counter > -2:
                    date = self._next_countdown_date(rec.irregular_start_date, date)
                    # Check holidays
                    if (
                        rec.holiday_start_time
                        and rec.holiday_end_time
                        and date >= rec.holiday_start_time
                        and date <= rec.holiday_end_time
                    ):
                        date = add_days_delta(date, 1)
                        continue
                    # Check temporary exemption
                    if (
                        rec.temporary_exempt_start_date
                        and rec.temporary_exempt_end_date
                        and date >= rec.temporary_exempt_start_date
                        and date <= rec.temporary_exempt_end_date
                    ):
                        date = add_days_delta(date, 1)
                        continue
                    # Otherwise
                    date = add_days_delta(date, 1)
                    counter -= 1
                rec.future_alert_date = self._next_countdown_date(
                    rec.irregular_start_date, date
                )

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
            # Only for irregular worker
            if rec.working_mode != "irregular" and not rec.irregular_start_date:
                rec.next_countdown_date = False
            # Holidays are not set properly
            elif bool(rec.holiday_start_time) != bool(rec.holiday_end_time):
                rec.next_countdown_date = False
            # Exemption have not a start and end time
            elif bool(rec.temporary_exempt_start_date) != bool(
                rec.temporary_exempt_end_date
            ):
                rec.next_countdown_date = False
            else:
                date = rec.today
                next_countdown_date = False
                while not next_countdown_date:
                    date = self._next_countdown_date(rec.irregular_start_date, date)
                    # Check holidays
                    if (
                        rec.holiday_start_time
                        and rec.holiday_end_time
                        and date >= rec.holiday_start_time
                        and date <= rec.holiday_end_time
                    ):
                        date = add_days_delta(date, 1)
                        continue
                    # Check temporary exemption
                    if (
                        rec.temporary_exempt_start_date
                        and rec.temporary_exempt_end_date
                        and date >= rec.temporary_exempt_start_date
                        and date <= rec.temporary_exempt_end_date
                    ):
                        date = add_days_delta(date, 1)
                        continue
                    # Otherwise
                    next_countdown_date = date
                rec.next_countdown_date = next_countdown_date

    #####################################
    #   Status Change implementation    #
    #####################################

    def _get_regular_status(self):
        """
        Return the value of the status
        for the regular worker
        """
        # TODO change
        ICP = self.env["ir.config_parameter"].sudo()
        alert_count = int(ICP.get_param("alert_count", -2))
        unsubscribed_count = int(ICP.get_param("unsubscribed_count", -4))
        default_alert_time = int(ICP.get_param("alert_time", 28))
        if (
            self.temporary_exempt_start_date
            and self.temporary_exempt_end_date
            and self.today >= self.temporary_exempt_start_date
            and self.today <= self.temporary_exempt_end_date
        ):
            return "exempted"
        if (
            self.holiday_start_time
            and self.holiday_end_time
            and self.today >= self.holiday_start_time
            and self.today <= self.holiday_end_time
        ):
            return "holiday"
        if self.sr >= 0:
            return "ok"

        if self.sr <= unsubscribed_count:
            return "unsubscribed"
        if self.sr <= alert_count and not self.alert_start_time:
            return "alert"
        if self.alert_start_time:
            if self.today < self.alert_start_time + timedelta(
                days=default_alert_time + self.time_extension
            ):
                return "alert"
            else:
                return "suspended"
        return "ok"

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
            self.cooperator_id.sudo().write({"subscribed_shift_ids": [(5, 0, 0)]})
            # Remove worker from supercoop in task_templates
            task_tpls = self.env["beesdoo.shift.template"].search(
                [("super_coop_id", "in", self.cooperator_id.user_ids.ids)]
            )
            task_tpls.write({"super_coop_id": False})
            # Remove worker for future tasks (remove also supercoop)
            self.env["beesdoo.shift.shift"].sudo().unsubscribe_from_today(
                self.cooperator_id, now=fields.Datetime.now()
            )
        if new_state == "alert":
            self.write({"alert_start_time": self.today})

    def _change_counter(self, data):
        """
        Call when a shift state is changed
        use data generated by _get_counter_date_state_change
        """
        self.sr += data.get("sr", 0)

    ############################################### # noqa
    ###### Irregular Cron implementation ########## # noqa
    ############################################### # noqa

    def _get_irregular_worker_domain(self, today):
        """
        return the domain the give the list
        of valid irregular worker that should
        get their counter changed by the cron
        """
        return [
            ("status", "not in", ["unsubscribed", "exempted", "resigning"]),
            ("irregular_start_date", "!=", False),
            ("working_mode", "!=", "exempt"),
        ]

    def _change_irregular_counter(self):
        """
        Define how the counter will change
        for the irregular worker
        where today - start_date is a multiple of the period
        by default 28 days
        """
        self.sr -= 1


# TODO: nombre de coop nécessaire pour remplir le planning
