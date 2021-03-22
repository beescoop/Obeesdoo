from odoo import api, _, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.subscribe.shift.exchange'
    _description = 'Subscribe Exchange shift'

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )
    # TODO : relational fields
    asked_timeslot_ids = fields.One2many(
        comodel_name='beesdoo.shift.template.dated',
        inverse_name='id',
        string='asked_timeslots'
    )
    exchanged_timeslot_id = fields.Many2one('beesdoo.shift.template.dated', string='exchanged_timeslot')
    request_date = fields.Date(required=True, string='date')