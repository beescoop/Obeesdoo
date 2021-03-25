from odoo import models, fields, api

class TimeslotsDate(models.Model):
    _name = 'beesdoo.shift.timeslots_date'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    shift_id = fields.Integer(compute='compute_shift')

    
