# -*- coding: utf-8 -*-
from openerp import models, fields, api

class TaskStage(models.Model):
    _name = 'beesdoo.shift.stage'
    _order = 'sequence asc'

    name = fields.Char()
    sequence = fields.Integer()
    color = fields.Integer()


class Task(models.Model):
    _name = 'beesdoo.shift.shift'

    _inherit = ['mail.thread']

    _order = "start_time asc"

    name = fields.Char(track_visibility='always')
    task_template_id = fields.Many2one('beesdoo.shift.template')
    planning_id = fields.Many2one(related='task_template_id.planning_id', store=True)
    task_type_id = fields.Many2one('beesdoo.shift.type', string="Task Type")
    worker_id = fields.Many2one('res.partner', track_visibility='onchange', domain=[('eater', '=', 'worker_eater')])
    start_time = fields.Datetime(track_visibility='always')
    end_time = fields.Datetime(track_visibility='always')
    stage_id = fields.Many2one('beesdoo.shift.stage', required=True, track_visibility='onchange')
    super_coop_id = fields.Many2one('res.users', string="Super Cooperative", domain=[('partner_id.super', '=', True)], track_visibility='onchange')
    color = fields.Integer(related="stage_id.color", readonly=True)
    is_regular = fields.Boolean(default=False)
    replaced_id = fields.Many2one('res.partner', track_visibility='onchange', domain=[('eater', '=', 'worker_eater')])

    def message_auto_subscribe(self, updated_fields, values=None):
        self._add_follower(values)
        return super(Task, self).message_auto_subscribe(updated_fields, values=values)

    def _add_follower(self, vals):
        if vals.get('worker_id'):
            worker = self.env['res.partner'].browse(vals['worker_id'])
            self.message_subscribe(partner_ids=worker.ids)

    @api.model
    def _read_group_stage_id(self, ids, domain, read_group_order=None, access_rights_uid=None):
        res  = self.env['beesdoo.shift.stage'].search([]).name_get()
        fold = dict.fromkeys([r[0] for r in res], False)
        return res, fold

    _group_by_full = {
        'stage_id': _read_group_stage_id,
    }

    #TODO button to replaced someone