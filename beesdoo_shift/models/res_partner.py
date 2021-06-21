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
    def future_shifts(self, end_date):

        start_date = datetime.now()

        shift_recset = self.env["beesdoo.shift.shift"]

        shift_recset |= (self.env["beesdoo.shift.shift"].sudo().search([
            ("start_time", ">", start_date.strftime("%Y-%m-%d %H:%M:%S"))
        ],
            order="start_time, task_template_id, task_type_id"))

        last_sequence = int(self.env["ir.config_parameter"].sudo().get_param("last_planning_seq"))

        next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)

        next_planning_date = fields.Datetime.from_string(
            self.env["ir.config_parameter"].sudo().get_param("next_planning_date", 0))

        shift_recset = self.env["beesdoo.shift.shift"]

        while next_planning_date < end_date:
            shift_recset |= next_planning.task_template_ids._generate_task_day()
            next_planning_date = next_planning._get_next_planning_date(next_planning_date)
            last_sequence = next_planning.sequence
            next_planning = self.env["beesdoo.shift.planning"]._get_next_planning(last_sequence)
            next_planning = next_planning.with_context(visualize_date=next_planning_date)

        return shift_recset


    def get_next_shifts(self,end_date):
        self.ensure_one()
        '''regular_next_shift_limit = int(
            self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.regular_next_shift_limit")
        )'''
        #nb_days = 28 * regular_next_shift_limit
        #start_date = datetime.now()
        #end_date = start_date + timedelta(days=nb_days)

        shifts = self.env["res.partner"].future_shifts(end_date)

        my_next_shifts=self.env["beesdoo.shift.shift"]
        for rec in shifts :
            if rec.worker_id.id == self.id :
                my_next_shifts |= rec

        return my_next_shifts

    # TODO access right + vue on res.partner
