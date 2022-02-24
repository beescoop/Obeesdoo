from odoo import api, fields, models

from odoo.addons.beesdoo_shift.models.cooperative_status import add_days_delta


class CooperativeStatus(models.Model):
    _inherit = "cooperative.status"
    _period = 28

    ######################################################
    #                                                    #
    #   Override of method to define status behavior     #
    #                                                    #
    ######################################################

    future_alert_date = fields.Date(compute="_compute_future_alert_date")
    next_countdown_date = fields.Date(compute="_compute_next_countdown_date")

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
            # Only for irregular worker
            if (
                rec.working_mode != "irregular"
                and not rec.irregular_start_date
            ):
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
                while counter > 0:
                    date = self._next_countdown_date(
                        rec.irregular_start_date, date
                    )
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
            if (
                rec.working_mode != "irregular"
                and not rec.irregular_start_date
            ):
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
                    date = self._next_countdown_date(
                        rec.irregular_start_date, date
                    )
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

    def write(self, vals):
        super(CooperativeStatus, self).write(vals)
        self._postpone_alert_start_time()

    def _get_regular_status(self):
        self.ensure_one()
        counter_unsubscribe = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("regular_counter_to_unsubscribe", -4)
        )
        alert_delay = int(
            self.env["ir.config_parameter"].sudo().get_param("alert_delay", 28)
        )
        grace_delay = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_grace_delay", 10)
        )
        ok = self.sr >= 0 and self.sc >= 0
        grace_delay = grace_delay + self.time_extension

        # check `holiday`
        if (
            self.holiday_start_time
            and self.holiday_end_time
            and self.today >= self.holiday_start_time
            and self.today <= self.holiday_end_time
        ):
            return "holiday"

        # check `exempted`.
        # Exempt end date is not required.
        elif (
            # Start and end are defined
            self.temporary_exempt_start_date
            and self.temporary_exempt_end_date
            and self.today >= self.temporary_exempt_start_date
            and self.today <= self.temporary_exempt_end_date
        ) or (
            # Only start is defined
            self.temporary_exempt_start_date
            and not self.temporary_exempt_end_date
            and self.today >= self.temporary_exempt_start_date
        ):
            return "exempted"

        # check `extension`
        # Transition to alert sr < 0 or stay in alert sr < 0 or sc < 0 and
        # thus alert time is defined
        elif (
            not ok
            and self.alert_start_time
            and self.extension_start_time
            and self.today
            <= add_days_delta(self.extension_start_time, grace_delay)
        ):
            return "extension"

        # check `unsubscribed`
        elif (self.sr + self.sc) <= counter_unsubscribe or self.unsubscribed:
            return "unsubscribed"

        # check `suspended`
        elif (
            not ok
            and self.alert_start_time
            and self.extension_start_time
            and self.today
            > add_days_delta(self.extension_start_time, grace_delay)
        ) or (
            not ok
            and self.alert_start_time
            and self.today > add_days_delta(self.alert_start_time, alert_delay)
        ):
            return "suspended"

        # check `alert`
        elif (self.sr < 0) or (not ok and self.alert_start_time):
            return "alert"

        # check `ok`
        elif ok or (not self.alert_start_time and self.sr >= 0):
            return "ok"

    def _get_irregular_status(self):
        self.ensure_one()
        counter_unsubscribe = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("irregular_counter_to_unsubscribe", -3)
        )
        alert_delay = int(
            self.env["ir.config_parameter"].sudo().get_param("alert_delay", 28)
        )
        grace_delay = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("default_grace_delay", 10)
        )
        ok = self.sr >= 0
        grace_delay = grace_delay + self.time_extension

        # check `holiday`
        if (
            self.holiday_start_time
            and self.holiday_end_time
            and self.today >= self.holiday_start_time
            and self.today <= self.holiday_end_time
        ):
            return "holiday"

        # check `exempted`
        # Exempt end date is not required.
        elif (
            # Start and end are defined
            self.temporary_exempt_start_date
            and self.temporary_exempt_end_date
            and self.today >= self.temporary_exempt_start_date
            and self.today <= self.temporary_exempt_end_date
        ) or (
            # Only start is defined
            self.temporary_exempt_start_date
            and not self.temporary_exempt_end_date
            and self.today >= self.temporary_exempt_start_date
        ):
            return "exempted"

        # check `extension`
        # Transition to alert sr < 0 or stay in alert sr < 0 or sc < 0 and
        # thus alert time is defined
        elif (
            not ok
            and self.alert_start_time
            and self.extension_start_time
            and self.today
            <= add_days_delta(self.extension_start_time, grace_delay)
        ):
            return "extension"

        # check `unsubscribed`
        elif self.sr <= counter_unsubscribe or self.unsubscribed:
            return "unsubscribed"

        # check `suspended`
        elif (
            not ok
            and self.alert_start_time
            and self.extension_start_time
            and self.today
            > add_days_delta(self.extension_start_time, grace_delay)
        ) or (
            not ok
            and self.alert_start_time
            and self.today > add_days_delta(self.alert_start_time, alert_delay)
        ):
            return "suspended"
        # check `alert`
        elif (self.sr < 0) or (not ok and self.alert_start_time):
            return "alert"

        # check `ok`
        elif ok or (not self.alert_start_time and self.sr >= 0):
            return "ok"

    def _state_change(self, new_state):
        self.ensure_one()
        if new_state == "alert":
            self.write(
                {
                    "alert_start_time": self.today,
                    "extension_start_time": False,
                    "time_extension": 0,
                }
            )
        if new_state == "ok":
            data = {"extension_start_time": False, "time_extension": 0}
            data["alert_start_time"] = False
            self.write(data)
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
                self.cooperator_id, now=fields.Datetime.now()
            )

    def _change_counter(self, data):
        """
        Call when a shift state is changed
        use data generated by _get_counter_date_state_change
        """
        self.sc += data.get("sc", 0)
        self.sr += data.get("sr", 0)
        self.irregular_absence_counter += data.get(
            "irregular_absence_counter", 0
        )
        self.irregular_absence_date = data.get("irregular_absence_date", False)

    ###############################################
    #        Irregular Cron implementation        #
    ###############################################

    def _get_irregular_worker_domain(self, **kwargs):
        today = kwargs.get("today") or self.today
        return [
            "&",
            "&",
            "&",
            ("status", "not in", ["unsubscribed", "exempted"]),
            ("working_mode", "=", "irregular"),
            ("irregular_start_date", "!=", False),
            "|",
            "|",
            ("holiday_start_time", "=", False),
            ("holiday_end_time", "=", False),
            "|",
            ("holiday_start_time", ">", today),
            ("holiday_end_time", "<", today),
        ]

    def _change_irregular_counter(self):
        if self.sr > 0:
            self.sr -= 1
        elif self.alert_start_time:
            self.sr -= 1
        else:
            self.sr -= 2

    ##################################
    #    Internal Implementation     #
    ##################################
    def _next_countdown_date(self, irregular_start_date, today=False):
        """
        Return the next countdown date given irregular_start_date and
        today dates.
        This does not take holiday and other status into account.
        """
        today = today or fields.Date.today()

        delta = (today - irregular_start_date).days
        if not delta % self._period:
            return today
        return add_days_delta(today, self._period - (delta % self._period))

    def _postpone_alert_start_time(self):
        """
        Postpone the alert_start_time based on holiday_end_time or
        temporary_exempt_end_date based on status.

        If alert_start_time is not set then nothing changes.
        """
        for rec in self:
            if (
                rec.status == "holiday"
                and rec.alert_start_time
                and rec.alert_start_time != rec.holiday_end_time
            ):
                rec.alert_start_time = rec.holiday_end_time
            elif (
                rec.status == "exempted"
                and rec.alert_start_time
                and rec.alert_start_time != rec.temporary_exempt_end_date
            ):
                rec.alert_start_time = rec.temporary_exempt_end_date
