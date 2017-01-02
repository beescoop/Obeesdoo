# -*- coding: utf-8 -*-
from openerp import models, fields, api


class InstanciatePlanning(models.TransientModel):
    _name = 'beesddoo.shift.generate_planning'

    def _get_planning(self):
        return self._context.get('active_id')

    date_start = fields.Date("First Day of planning", required=True)
    planning_id = fields.Many2one('beesdoo.shift.planning', readonly=True, default=_get_planning)

    @api.multi
    def generate_task(self):
        self.ensure_one()
        self = self.with_context(visualize_date=self.date_start)
        self.planning_id.task_template_ids._generate_task_day()
