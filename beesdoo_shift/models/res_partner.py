from datetime import datetime, timedelta

from pytz import timezone, utc

from odoo import _, api, fields, models


class ResPartner(models.Model):
    """
    One2many relationship with CooperativeStatus should
    be replaced by inheritance.
    """

    _inherit = "res.partner"
    # is_worker will be overriden in depending module
    # implementing the specific processes
    is_worker = fields.Boolean(string="Worker", readonly=False)
    can_shop = fields.Boolean(
        string="Is worker allowed to shop?",
        compute="_compute_can_shop",
        store=True,
    )
    # todo implement as delegated inheritance ?
    #  resolve as part of migration to OCA
    cooperative_status_ids = fields.One2many(
        string="Cooperative Statuses",
        comodel_name="cooperative.status",
        inverse_name="cooperator_id",
        readonly=True,
    )
    super = fields.Boolean(
        related="cooperative_status_ids.super",
        string="Super Cooperative",
        readonly=True,
        store=True,
    )
    info_session = fields.Boolean(
        related="cooperative_status_ids.info_session",
        string="Information Session ?",
        readonly=True,
        store=True,
    )
    info_session_date = fields.Date(
        related="cooperative_status_ids.info_session_date",
        string="Information Session Date",
        readonly=True,
        store=True,
    )
    working_mode = fields.Selection(
        related="cooperative_status_ids.working_mode",
        readonly=True,
        store=True,
    )
    exempt_reason_id = fields.Many2one(
        related="cooperative_status_ids.exempt_reason_id",
        readonly=True,
        store=True,
    )
    state = fields.Selection(
        related="cooperative_status_ids.status", readonly=True, store=True
    )
    extension_start_time = fields.Date(
        related="cooperative_status_ids.extension_start_time",
        string="Extension Start Day",
        readonly=True,
        store=True,
    )
    subscribed_shift_ids = fields.Many2many(
        comodel_name="beesdoo.shift.template", readonly=True
    )
    shift_shift_ids = fields.One2many(
        comodel_name="beesdoo.shift.shift",
        inverse_name="worker_id",
        string="Shifts",
        groups="beesdoo_shift.group_shift_attendance",
        help="All the shifts the worker is subscribed to.",
    )
    next_shift_id = fields.Many2one(
        related="cooperative_status_ids.next_shift_id",
        store=True,
    )
    is_subscribed_to_shift = fields.Boolean(
        related="cooperative_status_ids.is_subscribed_to_shift",
        store=True,
    )
    next_shift_date = fields.Datetime(
        related="cooperative_status_ids.next_shift_date",
        store=True,
    )

    @api.depends("cooperative_status_ids")
    def _compute_can_shop(self):
        """
        Shopping authorisation may vary on the can_shop status of the
        cooperative.status but also other parameters.
        Overwrite this function to change the default behavior.
        """
        for rec in self:
            if rec.cooperative_status_ids:
                rec.can_shop = rec.cooperative_status_ids.can_shop
            else:
                rec.can_shop = True

    @api.multi
    def coop_subscribe(self):
        return {
            "name": _("Subscribe Cooperator"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.subscribe",
            "target": "new",
        }

    @api.multi
    def coop_unsubscribe(self):
        res = self.coop_subscribe()
        res["context"] = {"default_unsubscribed": True}
        return res

    @api.multi
    def manual_extension(self):
        return {
            "name": _("Manual Extension"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.extension",
            "target": "new",
        }

    @api.multi
    def auto_extension(self):
        res = self.manual_extension()
        res["context"] = {"default_auto": True}
        res["name"] = _("Trigger Grace Delay")
        return res

    @api.multi
    def register_holiday(self):
        return {
            "name": _("Register Holiday"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.holiday",
            "target": "new",
        }

    @api.multi
    def temporary_exempt(self):
        return {
            "name": _("Temporary Exemption"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.temporary_exemption",
            "target": "new",
        }

    def write(self, vals):
        saved_vals = {}
        for rec in self:
            saved_vals[rec] = rec.subscribed_shift_ids
        result = super(ResPartner, self).write(vals)
        for rec in self:
            rec._update_shifts_on_subscribed_task_tmpl(
                prev_subscribed_task_tmpl=saved_vals[rec],
                cur_subscribed_task_tmpl=rec.subscribed_shift_ids,
            )
        return result

    def _update_shifts_on_subscribed_task_tmpl(
        self,
        prev_subscribed_task_tmpl,
        cur_subscribed_task_tmpl,
    ):
        """
        Subscribe or unsubscribe current partner from already generated
        shifts when subscribed_shift_ids changes.
        """
        self.ensure_one()
        shift_cls = self.env["beesdoo.shift.shift"]
        removed_tmpl_ids = prev_subscribed_task_tmpl - cur_subscribed_task_tmpl
        added_tmpl_ids = cur_subscribed_task_tmpl - prev_subscribed_task_tmpl
        if removed_tmpl_ids:
            shift_cls.unsubscribe_from_today(
                worker_ids=self,
                task_tmpl_ids=removed_tmpl_ids,
                now=datetime.now(),
            )
        if added_tmpl_ids:
            shift_cls.subscribe_from_today(
                worker_ids=self,
                task_tmpl_ids=added_tmpl_ids,
                now=datetime.now(),
            )

    def get_next_shifts(self):
        """
        Return next shifts of the worker without storing them into the database.
        :return: two beesdoo.shift.shift lists, the first one containing the
        already generated shifts, the second one containing the planned ones
        (empty for irregular workers)
        """
        self.ensure_one()
        now = datetime.now()
        subscribed_shifts_rec = (
            self.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                    ("worker_id", "=", self.id),
                ],
                order="start_time, task_template_id, task_type_id",
            )
        )
        # Create a list of record in order to add new record to it later
        generated_shifts = []
        for rec in subscribed_shifts_rec:
            generated_shifts.append(rec)

        planned_shifts = []

        if self.working_mode == "regular":
            # Compute main shift
            task_template = self.env["beesdoo.shift.template"].search(
                [("worker_ids", "in", self.id)], limit=1
            )

            if not task_template:
                return generated_shifts, []

            main_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("task_template_id", "=", task_template[0].id),
                    ("start_time", "!=", False),
                    ("end_time", "!=", False),
                ],
                order="start_time desc",
                limit=1,
            )

            if not main_shift:
                return generated_shifts, []

            # Get config
            regular_next_shift_limit = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("regular_next_shift_limit")
            )
            shift_period = int(
                self.env["ir.config_parameter"].sudo().get_param("shift_period")
            )
            next_planning_date = datetime.strptime(
                self.env["ir.config_parameter"].sudo().get_param("next_planning_date"),
                "%Y-%m-%d",
            )

            # Get temporary exemption
            status = self.cooperative_status_ids
            if status:
                exemption_start = status.temporary_exempt_start_date
                exemption_end = status.temporary_exempt_end_date

            for i in range(1, regular_next_shift_limit - len(generated_shifts) + 1):
                shift_date = self.add_days(main_shift.start_time, days=i * shift_period)
                if shift_date > next_planning_date:
                    # Check exemption
                    if (
                        exemption_start
                        and exemption_end
                        and shift_date.date() >= exemption_start
                        and shift_date.date() <= exemption_end
                    ):
                        continue

                    # Create the fictive shift
                    shift = main_shift.new()
                    shift.name = main_shift.name
                    shift.task_template_id = main_shift.task_template_id
                    shift.planning_id = main_shift.planning_id
                    shift.task_type_id = main_shift.task_type_id
                    shift.worker_id = main_shift.worker_id
                    shift.state = "open"
                    shift.super_coop_id = main_shift.super_coop_id
                    shift.color = main_shift.color
                    shift.is_regular = main_shift.is_regular
                    shift.replaced_id = main_shift.replaced_id
                    shift.revert_info = main_shift.revert_info
                    # Set new date
                    shift.start_time = self.add_days(
                        main_shift.start_time, days=i * shift_period
                    )
                    shift.end_time = self.add_days(
                        main_shift.end_time, days=i * shift_period
                    )
                    # Add the fictive shift to the list of shift
                    planned_shifts.append(shift)

        return generated_shifts, planned_shifts

    def add_days(self, datetime, days):
        """
        Add the number of days to datetime. This take the DST in
        account, meaning that the UTC time will be correct even if the
        new datetime has cross the DST boundary.

        :param datetime: a naive datetime expressed in UTC
        :return: a naive datetime expressed in UTC with the added days
        """
        # Ensure that the datetime given is without a timezone
        assert datetime.tzinfo is None
        # Get current user and user timezone
        # Take user tz, if empty use context tz, if empty use UTC
        cur_user = self.env["res.users"].search([("partner_id", "=", self.id)])
        user_tz = utc
        if cur_user.tz:
            user_tz = timezone(cur_user.tz)
        elif self.env.context["tz"]:
            user_tz = timezone(self.env.context["tz"])
        # Convert to UTC
        dt_utc = utc.localize(datetime, is_dst=False)
        # Convert to user TZ
        dt_local = dt_utc.astimezone(user_tz)
        # Add the number of days
        newdt_local = dt_local + timedelta(days=days)
        # If the newdt_local has cross the DST boundary, its tzinfo is
        # no longer correct. So it will be replaced by the correct one.
        newdt_local = user_tz.localize(newdt_local.replace(tzinfo=None))
        # Now the newdt_local has the right DST so it can be converted
        # to UTC.
        newdt_utc = newdt_local.astimezone(utc)
        return newdt_utc.replace(tzinfo=None)
