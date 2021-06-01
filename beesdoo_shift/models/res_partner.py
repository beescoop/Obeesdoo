from odoo import  _,api, fields, models
from pytz import timezone, utc
from datetime import timedelta,datetime

class ResPartner(models.Model):
    """
    One2many relationship with CooperativeStatus should
    be replaced by inheritance.
    """

    _inherit = "res.partner"

    worker_store = fields.Boolean(default=False)
    is_worker = fields.Boolean(
        related="worker_store", string="Worker", readonly=False
    )
    can_shop = fields.Boolean(
        string="Is worker allowed to shop?",
        compute="_compute_can_shop",
        store=True,
    )
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

    @api.multi
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
        #cur_user = self.env["res.users"].browse(self.uid)
        #cur_user = self.id
        user_tz = utc
        if self.tz:
            user_tz = timezone(self.tz)
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

    @api.multi
    def my_next_shift(self):
        """
        Return template variables for
        'beesdoo_website_shift.my_shift_next_shifts' template
        """
        # Get current user
        cur_user = self.id
        # Get shifts where user is subscribed
        now = datetime.now()
        subscribed_shifts_rec = (
            self.env["beesdoo.shift.shift"]
                .sudo()
                .search(
                [
                    ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                    ("worker_id", "=", cur_user),
                ],
                order="start_time, task_template_id, task_type_id",
            )
        )
        # Create a list of record in order to add new record to it later
        #subscribed_shifts = []
        subscribed_shifts = self.env["beesdoo.shift.shift"]
        for rec in subscribed_shifts_rec:
            subscribed_shifts |= rec

        # In case of regular worker, we compute his fictive next shifts
        # according to the regular_next_shift_limit
        if self.working_mode == 'regular':
            # Compute main shift
            nb_subscribed_shifts = len(subscribed_shifts)
            if nb_subscribed_shifts > 0:
                main_shift = subscribed_shifts[-1]
            else:
                task_template = (
                    self.env["beesdoo.shift.template"]
                        .sudo()
                        .search(
                        [("worker_ids", "in", cur_user)], limit=1
                    )
                )
                main_shift = (
                    self.env["beesdoo.shift.shift"]
                        .sudo()
                        .search(
                        [
                            ("task_template_id", "=", task_template[0].id),
                            ("start_time", "!=", False),
                            ("end_time", "!=", False),
                        ],
                        order="start_time desc",
                        limit=1,
                    )
                )
            # Get config
            #regular_next_shift_limit = self.website.regular_next_shift_limit
            regular_next_shift_limit = 7
            shift_period = int(
                self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("beesdoo_shift.shift_period")
            )

            for i in range(nb_subscribed_shifts, regular_next_shift_limit):
                # Create the fictive shift
                shift = main_shift.new()
                shift.name = main_shift.name
                #TODO : faire checker changement
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
                subscribed_shifts |= shift

        return subscribed_shifts

    # TODO access right + vue on res.partner
