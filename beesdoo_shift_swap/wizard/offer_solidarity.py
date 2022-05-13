from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OfferSolidarityShift(models.TransientModel):
    _name = "beesdoo.shift.offer.solidarity.shift"
    _description = "Offer solidarity shift"

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        string="Cooperator",
        required=True,
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="Shift",
        required=True,
        domain=[
            ("date", ">", datetime.now()),
        ],
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

    @api.onchange("worker_id")
    def _get_template_dated(self):
        for record in self:
            tmpl_dated = self.env["beesdoo.shift.template.dated"].get_next_tmpl_dated()
            tmpl_dated_possible = tmpl_dated.remove_already_subscribed_shifts(
                record.worker_id
            )
            tmpl_dated_wanted = self.env["beesdoo.shift.template.dated"]
            for template in tmpl_dated_possible:
                tmpl_dated_wanted |= tmpl_dated_wanted.create(
                    {
                        "template_id": template.template_id.id,
                        "date": template.date,
                        "store": False,
                    }
                )
            return {"domain": {"tmpl_dated_id": [("id", "in", tmpl_dated_wanted.ids)]}}

    @api.multi
    def create_offer(self):
        self._check()
        data = {
            "worker_id": self.worker_id.id,
            "tmpl_dated_id": self.tmpl_dated_id.id,
        }
        self.env["beesdoo.shift.solidarity.offer"].sudo().create(data)
