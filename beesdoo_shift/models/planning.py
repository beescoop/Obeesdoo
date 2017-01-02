# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import UserError

from pytz import UTC
import math
from datetime import datetime, timedelta

def float_to_time(f):
    decimal, integer = math.modf(f)
    return "%s:%s" % (str(int(integer)).zfill(2), str(int(round(decimal * 60))).zfill(2))

def floatime_to_hour_minute(f):
    decimal, integer = math.modf(f)
    return int(integer), int(round(decimal * 60))

def get_first_day_of_week():
    today = datetime.now()
    return datetime.now() - timedelta(days=today.weekday())

class TaskType(models.Model):
    _name = 'beesdoo.shift.type'

    name = fields.Char()
    description = fields.Text()
    active = fields.Boolean(default=True)

class DayNumber(models.Model):
    _name = 'beesdoo.shift.daynumber'
    
    _order = 'number asc'

    name = fields.Char()
    number = fields.Integer("Day Number", help="From 1 to N, When you will instanciate your planning, Day 1 will be the start date of the instance, Day 2 the second, etc...")
    active = fields.Boolean(default=True)

class Planning(models.Model):
    _name = 'beesdoo.shift.planning'

    name = fields.Char()
    task_template_ids = fields.One2many('beesdoo.shift.template', 'planning_id')

class TaskTemplate(models.Model):
    _name = 'beesdoo.shift.template'

    name = fields.Char(required=True)
    planning_id = fields.Many2one('beesdoo.shift.planning', required=True)
    day_nb_id = fields.Many2one('beesdoo.shift.daynumber', string='Day', required=True)
    task_type_id = fields.Many2one('beesdoo.shift.type', string="Type")
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)

    duration = fields.Float(help="Duration in Hour")
    worker_nb = fields.Integer(string="Number of worker", help="Max number of worker for this task", default=1)
    worker_ids = fields.Many2many('res.partner', string="Recurrent worker assigned", domain=[('eater', '=', 'worker_eater')])
    remaining_worker = fields.Integer(compute="_get_remaining", store=True, string="Remaining Place")
    active = fields.Boolean(default=True)
    #For Kanban View Only
    color = fields.Integer('Color Index')
    worker_name = fields.Char(compute="_get_worker_name")
    #For calendar View
    start_date = fields.Datetime(compute="_get_fake_date", search="_dummy_search")
    end_date = fields.Datetime(compute="_get_fake_date", search="_dummy_search")

    @api.depends('start_time', 'end_time')
    def _get_fake_date(self):
        today = datetime.strptime(self._context.get('visualize_date'), '%Y-%m-%d') if self._context.get('visualize_date') else get_first_day_of_week()
        for rec in self:
            day = today + timedelta(days=rec.day_nb_id.number - 1)
            h_begin, m_begin = floatime_to_hour_minute(rec.start_time)
            h_end, m_end = floatime_to_hour_minute(rec.end_time)
            rec.start_date = fields.Datetime.context_timestamp(self, day).replace(hour=h_begin, minute=m_begin, second=0).astimezone(UTC)
            rec.end_date = fields.Datetime.context_timestamp(self, day).replace(hour=h_end, minute=m_end, second=0).astimezone(UTC)
    
    def _dummy_search(self, operator, value):
        return []

    @api.depends('worker_ids', 'worker_nb')
    def _get_remaining(self):
        for rec in self:
            rec.remaining_worker =  rec.worker_nb - len(rec.worker_ids)

    @api.depends("worker_ids")
    def _get_worker_name(self):
        for rec in self:
            rec.worker_name = ','.join(rec.worker_ids.mapped('display_name'))
    
    @api.constrains('worker_nb', 'worker_ids')
    def _nb_worker_max(self):
        for rec in self:
            if len(rec.worker_ids) > rec.worker_nb:
                raise UserError(_('you cannot assign more worker then the number maximal define on the template'))


    @api.onchange('start_time', 'end_time')
    def _get_duration(self):
        if self.start_time and self.end_time:
            self.duration = self.end_time - self.start_time
    
    @api.onchange('duration')
    def _set_duration(self):
        if self.start_time:
            self.end_time = self.start_time +self.duration

    def _generate_task_day(self):
        tasks = self.env['beesdoo.shift.shift']
        for rec in self:
            for i in xrange(0, rec.worker_nb):
                tasks |= tasks.create({
                    'name' :  "%s (%s) - (%s) [%s]" % (rec.name, float_to_time(rec.start_time), float_to_time(rec.end_time), i),
                    'task_template_id' : rec.id,
                    'task_type_id' : rec.task_type_id.id,
                    'worker_id' : rec.worker_ids[i].id if len(rec.worker_ids) > i else False,
                    'start_time' : rec.start_date,
                    'end_time' :  rec.end_date,
                })
        return tasks