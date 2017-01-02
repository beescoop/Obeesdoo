# -*- coding: utf-8 -*-
from openerp import models, fields

STATES = [
    ('draft', 'Unconfirmed'),
    ('open', 'Confirmed'),
    ('done', 'Attended'),
    ('absent', 'Absent'),
    ('excused', 'Excused'),
    ('replaced', 'Replaced'),
    ('cancel', 'Cancelled'),
]

class Task(models.Model):
    _name = 'beesdoo.shift.shift'

    #EX01 ADD inheritance
    _inherit = ['mail.thread']

    name = fields.Char(track_visibility='always')
    task_template_id = fields.Many2one('beesdoo.shift.template')
    planning_id = fields.Many2one(related='task_template_id.planning_id', store=True)
    task_type_id = fields.Many2one('beesdoo.shift.type', string="Task Type")
    worker_id = fields.Many2one('res.partner', track_visibility='onchange', domain=[('eater', '=', 'worker_eater')])
    start_time = fields.Datetime(track_visibility='always')
    end_time = fields.Datetime(track_visibility='always')
    state = fields.Selection(STATES, default='draft', track_visibility='onchange')

    def message_auto_subscribe(self, updated_fields, values=None):
        self._add_follower(values)
        return super(Task, self).message_auto_subscribe(updated_fields, values=values)

    def _add_follower(self, vals):
        if vals.get('worker_id'):
            worker = self.env['res.partner'].browse(vals['worker_id'])
            self.message_subscribe(partner_ids=worker.ids)