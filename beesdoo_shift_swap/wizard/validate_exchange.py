from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel):
    _name = "beesdoo.shift.validate.shift.exchange"
    _description = "Validate Shift Exchange"

    my_proposition = fields.Many2one(
        "beesdoo.shift.exchange_request",
        default=lambda self: self.env["beesdoo.shift.exchange_request"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="My proposition",
    )

    match_proposition = fields.Many2one(
        "beesdoo.shift.exchange_request",
        string="Match proposition",
        required=True,
    )

    @api.onchange("my_proposition")
    def _get_possible_match(self):
        for record in self:
            if (
                not record.my_proposition.exchanged_tmpl_dated_id
                or not record.my_proposition.asked_tmpl_dated_ids
            ):
                record.match_proposition = False
            else:
                exchanges = self.env["beesdoo.shift.exchange_request"].matching_request(
                    record.my_proposition.asked_tmpl_dated_ids,
                    record.my_proposition.exchanged_tmpl_dated_id,
                )
                return {"domain": {"match_proposition": [("id", "in", exchanges.ids)]}}

    def _check(self, group="shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(_("You don't have the required access for this operation."))
        if (
            self.my_proposition.worker_id == self.env.user.partner_id
            and not self.env.user.has_group("shift.group_cooperative_admin")
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    def validate_match(self):
        self = self._check()
        self.env["beesdoo.shift.exchange"].sudo().create(
            {
                "first_request_id": self.my_proposition.id,
                "second_request_id": self.match_proposition.id,
            }
        )
