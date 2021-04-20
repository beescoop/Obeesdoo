from odoo import api, exceptions, fields, models

class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.subscribe.shift.swap'
    _description = 'Subscribe swap shift'

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="Cooperator",
    )

    exchanged_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='Unwanted Shift'
    )

    comfirmed_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='Underpopulated Shift'
    )



