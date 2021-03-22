from odoo import models, fields, api

class subscribe_underpopulated_shift(models.Model):
    _name = 'beesdoo.shift.subscribed_underpopulated_shift'

    exchanged_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='exchanged_shift'
    )
    comfirmed_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='asked_shift'
    )
    date = fields.Date(required = True)
    status = fields.Char(compute = 'compute_status')



