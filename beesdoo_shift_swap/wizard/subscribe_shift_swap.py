from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel):
    _name = "beesdoo.shift.subscribe.shift.swap"
    _description = "Subscribe swap shift"

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Unwanted Shift",
        required=True,
    )

    wanted_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Underpopulated Shift",
        required=True,
    )

    @api.onchange("worker_id")
    def _get_exchangeable_template_dated(self):
        for record in self:
            tmpl_dated = record.worker_id.get_next_tmpl_dated()
            tmpl_dated_possible = self.env["beesdoo.shift.template.dated"]
            for template in tmpl_dated:
                tmpl_dated_possible |= tmpl_dated_possible.create(
                    {
                        "template_id": template.template_id.id,
                        "date": template.date,
                        "store": False,
                    }
                )
            return {
                "domain": {
                    "exchanged_tmpl_dated_id": [("id", "in", tmpl_dated_possible.ids)]
                }
            }

    @api.onchange("exchanged_tmpl_dated_id")
    def _get_available_tmpl_dated(self):
        for record in self:
            if not record.exchanged_tmpl_dated_id:
                record.wanted_tmpl_dated_id = False
            else:
                tmpl_dated = self.env["beesdoo.shift.swap"].get_underpopulated_shift()
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

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "beesdoo_shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    @api.multi
    def make_change(self):
        self = self._check()
        self.worker_id.check_shift_number_limit(self.wanted_tmpl_dated_id)
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
        record = self.env["beesdoo.shift.swap"].sudo().create(data)
        if record._compute_exchanged_already_generated():
            record.unsubscribe_shift()
        if record._compute_comfirmed_already_generated():
            record.subscribe_shift()
