from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel):
    _name = "beesdoo.shift.subscribe.shift.swap"
    _description = "Subscribe swap shift"

    @api.onchange("worker_id")
    def onchange_exchanged_tmpl_dated(self):
        # TODO : prendre en compte qd il est inscris a aucun shift
        for record in self:
            if not record.worker_id:
                record.exchanged_tmpl_dated_id = False
            else:
                tmpl_dated = record.worker_id.get_next_tmpl_dated()
                # record.available_tmpl_dated = tmpl_dated
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in tmpl_dated:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create(
                        {
                            "template_id": template.id,
                            "date": date,
                            "store": False,
                        }
                    )
                return {"domain": {"exchanged_tmpl_dated_id": [("id", "in", temp.ids)]}}

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    @api.onchange("exchanged_tmpl_dated_id")
    def _get_available_tmpl_dated(self):
        for record in self:
            if not record.exchanged_tmpl_dated_id:
                record.wanted_tmpl_dated_id = False
            else:
                tmpl_dated = self.env[
                    "beesdoo.shift.subscribed_underpopulated_shift"
                ].get_underpopulated_shift()
                # record.available_tmpl_dated = tmpl_dated
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in tmpl_dated:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create(
                        {
                            "template_id": template.id,
                            "date": date,
                            "store": False,
                        }
                    )
                return {"domain": {"wanted_tmpl_dated_id": [("id", "in", temp.ids)]}}

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Unwanted Shift",
    )

    wanted_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Underpopulated Shift",
    )

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "beesdoo_shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    # TODO : check si il a pas fais un échange 2mois avant
    def has_already_done_exchange(self):
        worker_id = self.worker_id
        cur_date = datetime.now()
        limit_date = cur_date - timedelta(2 * 28)
        swaps = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search(
            [
                ("date", "<=", cur_date),
                ("date", ">=", limit_date),
            ]
        )
        for swap in swaps:
            if (
                swap.worker_id == worker_id
                and self.exchanged_tmpl_dated_id == swap.wanted_tmpl_dated_id
            ):
                return True
            return False

    @api.multi
    def make_change(self):
        self = self._check()
        if self.has_already_done_exchange():
            raise UserError(_("You already swap your shift in the last 2months"))
        self.env["beesdoo.shift.template.dated"].check_possibility_to_exchange(
            self.wanted_tmpl_dated_id, self.worker_id
        )
        self.exchanged_tmpl_dated_id.store = True
        self.wanted_tmpl_dated_id.store = True
        data = {
            "date": datetime.date(datetime.now()),
            "worker_id": self.worker_id.id,
            "exchanged_tmpl_dated_id": self.exchanged_tmpl_dated_id.id,
            "wanted_tmpl_dated_id": self.wanted_tmpl_dated_id.id,
        }
        useless_tmpl_dated = self.env["beesdoo.shift.template.dated"].search(
            [("store", "=", False)]
        )
        useless_tmpl_dated.unlink()
        record = (
            self.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .create(data)
        )
        if record._compute_exchanged_already_generated():
            record.unsubscribe_shift()
        if record._compute_comfirmed_already_generated():
            record.subscribe_shift()
