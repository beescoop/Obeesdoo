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

    match_proposition = fields.Many2one(
        'beesdoo.shift.exchange_request',
        string='possible match',
    )

