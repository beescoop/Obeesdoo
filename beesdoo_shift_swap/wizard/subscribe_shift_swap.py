from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel):
    _name = "beesdoo.shift.subscribe.shift.swap"
    _description = "Swap shift wizard"

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
        string="Wanted Shift",
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

    @api.onchange("worker_id")
    def _get_possible_tmpl_dated(self):
        for record in self:
            available_tmpl_dated = self.env[
                "beesdoo.shift.template.dated"
            ].get_available_tmpl_dated()
            tmpl_dated_possible = available_tmpl_dated.remove_already_subscribed_shifts(
                record.worker_id
            )
            tmpl_dated_wanted = self.env["beesdoo.shift.template.dated"]
            for rec in tmpl_dated_possible:
                tmpl_dated_wanted |= tmpl_dated_wanted.create(
                    {
                        "template_id": rec.template_id.id,
                        "date": rec.date,
                        "store": False,
                    }
                )
            return {
                "domain": {
                    "wanted_tmpl_dated_id": [("id", "in", tmpl_dated_wanted.ids)]
                }
            }

    def _check(self, group="shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if self.worker_id == self.env.user.partner_id and not self.env.user.has_group(
            "shift.group_cooperative_admin"
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    @api.multi
    def create_swap(self):
        self = self._check()
        self.worker_id.check_shift_number_limit(self.wanted_tmpl_dated_id)
        self.exchanged_tmpl_dated_id.store = True
        self.wanted_tmpl_dated_id.store = True
        useless_tmpl_dated = self.env["beesdoo.shift.template.dated"].search(
            [("store", "=", False)]
        )
        useless_tmpl_dated.unlink()
        data = {
            "worker_id": self.worker_id.id,
            "exchanged_tmpl_dated_id": self.exchanged_tmpl_dated_id.id,
            "wanted_tmpl_dated_id": self.wanted_tmpl_dated_id.id,
        }
        self.env["beesdoo.shift.swap"].sudo().create(data)
