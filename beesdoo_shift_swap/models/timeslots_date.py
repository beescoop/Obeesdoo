from odoo import models, fields, api

class TimeslotsDate(models.Model):
    _name = 'beesdoo.shift.timeslots_date'

    date = fields.Datetime(required = True)
    template_id = fields.Many2one("beesdoo.shift.template")
    #shift_id = fields.Integer(compute='compute_shift')


    def swap_shift_to_timeslot(self,shift):
        timeslot= self.env["beesdoo.shift.timeslots_date"].create()
        timeslot.date = shift.start_time
        timeslot.template_id = shift.task_template_id


    
