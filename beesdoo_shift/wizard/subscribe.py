from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StatusActionMixin(models.AbstractModel):
    _name = "beesdoo.shift.action_mixin"
    _description = "beesdoo.shift.action_mixin"

    cooperator_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
    )

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if (
            self.cooperator_id == self.env.user.partner_id
            and not self.env.user.has_group("beesdoo_shift.group_cooperative_admin")
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)


class Subscribe(models.TransientModel):
    _name = "beesdoo.shift.subscribe"
    _description = "beesdoo.shift.subscribe"
    _inherit = "beesdoo.shift.action_mixin"

    def _get_date(self):
        date = (
            self.env["res.partner"]
            .browse(self._context.get("active_id"))
            .info_session_date
        )
        if not date:
            return fields.Date.today()
        else:
            return date

    def _get_info_session_date(self):
        date = (
            self.env["res.partner"]
            .browse(self._context.get("active_id"))
            .info_session_date
        )
        if date and self._get_info_session_followed():
            return date
        else:
            return False

    def _get_info_session_followed(self):
        session_followed = (
            self.env["res.partner"].browse(self._context.get("active_id")).info_session
        )
        return session_followed

    def _get_shift(self):
        shifts = (
            self.env["res.partner"]
            .browse(self._context.get("active_id"))
            .subscribed_shift_ids
        )
        if shifts:
            return shifts[0]
        return

    def _get_nb_shifts(self):
        return len(
            self.env["res.partner"]
            .browse(self._context.get("active_id"))
            .subscribed_shift_ids
        )

    def _get_super(self):
        return self.env["res.partner"].browse(self._context.get("active_id")).super

    def _get_mode(self):
        return (
            self.env["res.partner"].browse(self._context.get("active_id")).working_mode
        )

    def _get_reset_counter_default(self):
        partner = self.env["res.partner"].browse(self._context.get("active_id"))
        return partner.state == "unsubscribed" and partner.working_mode == "regular"

    info_session = fields.Boolean(
        string="Followed an information session",
        default=_get_info_session_followed,
    )
    info_session_date = fields.Date(
        string="Date of information session", default=_get_info_session_date
    )
    super = fields.Boolean(string="Super Cooperator", default=_get_super)
    working_mode = fields.Selection(
        [
            ("regular", "Regular worker"),
            ("irregular", "Irregular worker"),
            ("exempt", "Exempted"),
        ],
        default=_get_mode,
    )
    exempt_reason_id = fields.Many2one("cooperative.exempt.reason", "Exempt Reason")
    shift_id = fields.Many2one("beesdoo.shift.template", default=_get_shift)
    nb_shifts = fields.Integer(string="Number of shifts", default=_get_nb_shifts)
    reset_counter = fields.Boolean(default=_get_reset_counter_default)
    reset_compensation_counter = fields.Boolean(default=False)
    unsubscribed = fields.Boolean(
        default=False,
        string="Are you sure to remove this cooperator from his subscribed shift ?",
    )
    irregular_start_date = fields.Date(string="Start Date", default=fields.Date.today)
    resigning = fields.Boolean(default=False, help="Want to leave the beescoop")

    @api.multi
    def unsubscribe(self):
        self = self._check()
        if not self.unsubscribed:
            return

        status_id = self.env["cooperative.status"].search(
            [("cooperator_id", "=", self.cooperator_id.id)]
        )
        data = {
            "unsubscribed": True,
            "cooperator_id": self.cooperator_id.id,
            "resigning": self.resigning,
        }
        if status_id:
            status_id.sudo().write(data)
        else:
            self.env["cooperative.status"].sudo().create(data)

    @api.multi
    def subscribe(self):
        self = self._check()
        if self.shift_id and self.shift_id.remaining_worker <= 0:
            raise UserError(_("There is no remaining spot in this shift"))

        # cleanup previous shift template subscriptions
        self.cooperator_id.sudo().write({"subscribed_shift_ids": [(5,)]})

        data = {
            "info_session": self.info_session,
            "info_session_date": self.info_session_date,
            "working_mode": self.working_mode,
            "exempt_reason_id": self.exempt_reason_id.id,
            "super": self.super,
            "cooperator_id": self.cooperator_id.id,
            "unsubscribed": False,
            "irregular_start_date": self.irregular_start_date,
            "irregular_absence_date": False,
            "irregular_absence_counter": 0,
        }
        if self.reset_counter:
            data["sr"] = 0
            data["extension_start_time"] = False
            data["alert_start_time"] = False
            data["time_extension"] = 0
        if self.reset_compensation_counter:
            data["sc"] = 0

        coop_status_obj = self.env["cooperative.status"]
        status_id = coop_status_obj.search(
            [("cooperator_id", "=", self.cooperator_id.id)]
        )
        if status_id:
            status_id.sudo().write(data)
        else:
            status_id = coop_status_obj.sudo().create(data)
            # Normally the write method is not necessary here.
            # But it does not work without it. You have to make 2 registration
            # to a shift to keep information like "Worker mode, session info
            # ,...
            status_id.sudo().write(data)

        # add the new shift template
        if self.shift_id and self.working_mode == "regular":
            self.cooperator_id.sudo().write(
                {"subscribed_shift_ids": [(4, self.shift_id.id, False)]}
            )
        return True
