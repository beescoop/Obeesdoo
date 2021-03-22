from odoo import api, _, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.validate.shift.exchange'
    _description = 'Validate Shift Exchange'

    my_proposition = fields.Many2one(
        "beesdoo.shift.exchange_request",
        default=lambda self: self.env["beesdoo.shift.exchange_request"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="My proposition",
    )

    @api.onchange('my_proposition')
    def get_possible_match(self):
        for record in self:
            if not record.my_proposition.exchanged_timeslot_id or not record.my_proposition.asked_timeslot_ids:
                record.match_proposition = False
            else:
                exchanges = self.env["beesdoo.shift.exchange_request"].matching_request(record.my_proposition.asked_timeslot_ids,
                                                                                        record.my_proposition.exchanged_timeslot_id)
                return {
                    'domain': {'match_proposition': [('id', 'in', exchanges.ids)]}
                }

    match_proposition = fields.Many2one(
        'beesdoo.shift.exchange_request',
        string='Match proposition',
    )

    def _check(self, group="beesdoo_shift.group_shift_management"):
        self.ensure_one()
        if not self.env.user.has_group(group):
            raise UserError(
                _("You don't have the required access for this operation.")
            )
        if (
            self.my_proposition.worker_id == self.env.user.partner_id
            and not self.env.user.has_group(
                "beesdoo_shift.group_cooperative_admin"
            )
        ):
            raise UserError(_("You cannot perform this operation on yourself"))
        return self.with_context(real_uid=self._uid)

    def validate_match(self):
        self = self._check()
        exchange_data = {
            "first_request_id": self.my_proposition.id,
            "second_request_id": self.match_proposition.id,
        }
        exchange = self.env["beesdoo.shift.exchange"].sudo().create(exchange_data)
        data={
            "validate_request":self.match_proposition.id,
            "exchange_id":exchange.id,
            "status":'done'
        }
        self.my_proposition.write(data)
        self.match_proposition.write(
            {'status': 'done'}
        )
        if self.env["beesdoo.shift.exchange"].is_shift_generated(self.my_proposition):
            self.env["beesdoo.shift.exchange"].subscribe_exchange_to_shift(self.my_proposition)
            exchange.write({
                "first_shift_status":True
            })
        if self.env["beesdoo.shift.exchange"].is_shift_generated(self.match_proposition):
            self.env["beesdoo.shift.exchange"].subscribe_exchange_to_shift(self.match_proposition)
            exchange.write({
                "second_shift_status":True
            })