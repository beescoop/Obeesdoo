# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import UserError
import json

class TaskStage(models.Model):
    _name = 'beesdoo.shift.stage'
    _order = 'sequence asc'

    name = fields.Char()
    sequence = fields.Integer()
    color = fields.Integer()
    code = fields.Char(readonly=True)

    @api.multi
    def unlink(self):
        raise UserError(_("You Cannot delete Task Stage"))


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
    revert_info = fields.Text()

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
    @api.model
    def unsubscribe_from_today(self, worker_ids, today=None):
        today = today or fields.Date.today()
        today = today + ' 00:00:00'
        to_unsubscribe = self.search([('worker_id', 'in', worker_ids), ('start_time', '>=', today)])
        to_unsubscribe.write({'worker_id': False, 'is_regular': False})
        #What about replacement ?
        #Remove worker, replaced_id and regular
        to_unsubscribe_replace = self.search([('replaced_id', 'in', worker_ids), ('start_time', '>=', today)])
        to_unsubscribe_replace.write({'worker_id': False, 'is_regular': False, 'replaced_id': False})

    @api.multi
    def write(self, vals):
        """
            Overwrite write to track stage change
        """
        if 'stage_id' in vals:
            for rec in self:
                if vals['stage_id'] != rec.stage_id.id:
                    rec._update_stage(rec.stage_id.id, vals['stage_id'])
        return super(Task, self).write(vals)

    def _set_revert_info(self, data, status):
        data = {
            'status_id': status.id,
            'data' : {k: data[k] * -1 for k in data.keys()}
        }
        self.write({'revert_info': json.dumps(data)})

    def _revert(self):
        if not self.revert_info:
            return
        try:
            data = json.loads(self.revert_info)
            self.env['cooperative.status'].browse(data['status_id'])._change_counter(data['data'])
        except:
            pass

    def _update_stage(self, old_stage, new_stage):
        self.ensure_one()
        self._revert()
        update = int(self.env['ir.config_parameter'].get_param('always_update', False))
        if not (self.worker_id or self.replaced_id) or update:
            return
        new_stage = self.env['beesdoo.shift.stage'].browse(new_stage)

        if not self.replaced_id: #No replacement case
            status = self.worker_id.cooperative_status_ids[0]
        else:
            status = self.replaced_id.cooperative_status_ids[0]

        data = {}
        if new_stage == self.env.ref('beesdoo_shift.done') and self.is_regular:
            pass
        if new_stage == self.env.ref('beesdoo_shift.done') and not self.is_regular:
            if status.sr < 0:
                data['sr'] = 1
            elif status.sc < 0:
                data['sc'] = 1
            else:
                data['sr'] = 1

        if new_stage == self.env.ref('beesdoo_shift.absent') and not self.replaced_id:
            data['sr'] = - 1
            if status.sr <= 0:
                data['sc'] = -1
        if new_stage == self.env.ref('beesdoo_shift.absent') and self.replaced_id:
            data['sr'] = -1

        if new_stage == self.env.ref('beesdoo_shift.excused'):
            data['sr'] = -1

        status.sudo()._change_counter(data)
        self._set_revert_info(data, status)
