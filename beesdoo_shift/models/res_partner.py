from datetime import datetime, timedelta

from odoo import _, api, fields, models


class ResPartner(models.Model):
    """
    One2many relationship with CooperativeStatus should
    be replaced by inheritance.
    """

    _inherit = "res.partner"
    worker_store = fields.Boolean(default=False)
    # is_worker will be overriden in depending module
    # implementing the specific processes
    is_worker = fields.Boolean(related="worker_store", string="Worker", readonly=False)
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

    @api.multi
    def display_future_shift(self, end_date):

        start_date = datetime.now()

        shift_recset = self.env["beesdoo.shift.shift"]

        shift_recset |= (
            self.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [("start_time", ">", start_date.strftime("%Y-%m-%d %H:%M:%S"))],
                order="start_time, task_template_id, task_type_id",
            )
        )

        last_sequence = int(
            self.env["ir.config_parameter"].sudo().get_param("last_planning_seq")
        )

        next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(
            last_sequence
        )

        next_planning_date = fields.Datetime.from_string(
            self.env["ir.config_parameter"].sudo().get_param("next_planning_date", 0)
        )

        next_planning = next_planning.with_context(visualize_date=next_planning_date)

        shift_recset = self.env["beesdoo.shift.shift"]

        while next_planning_date < end_date:
            shift_recset |= next_planning.task_template_ids.get_task_day()
            next_planning_date = next_planning._get_next_planning_date(
                next_planning_date
            )
            last_sequence = next_planning.sequence
            next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(
                last_sequence
            )
            next_planning = next_planning.with_context(
                visualize_date=next_planning_date
            )

        return shift_recset

    def my_next_shift(self):
        # Get current user
        cur_user = self.id
        regular_next_shift_limit = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.regular_next_shift_limit")
        )
        nb_days = 28 * regular_next_shift_limit
        start_date = datetime.now()
        end_date = start_date + timedelta(days=nb_days)

        shifts = self.env["res.partner"].display_future_shift(end_date)

        my_next_shifts = self.env["beesdoo.shift.shift"]
        for rec in shifts:
            if rec.worker_id.id == cur_user:
                my_next_shifts |= rec

        return my_next_shifts
