from odoo import api, exceptions, fields, models



class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.subscribe.shift.swap'
    _description = 'Subscribe swap shift'

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    exchanged_timeslot_id = fields.Many2one(
        'beesdoo.shift.timeslots_date',
        string='Unwanted Shift'
    )

    comfirmed_timeslot_id = fields.Many2one(
        'beesdoo.shift.timeslots_date',
        string='Underpopulated Shift'
    )


    '''
    @api.onchange('comfirmed_timeslot_id')
    def onchange_underpopulated_shift(self):
        my_shift = self.exchanged_timeslot_id
        my_possibility = self.env["beesdoo.shift.subscribed_underpopulated_shift"].display_underpopulated_shift(my_shift)

    '''




