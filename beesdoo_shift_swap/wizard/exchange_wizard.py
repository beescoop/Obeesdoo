from odoo import api, _, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class SubscribeShiftSwap(models.TransientModel) :
    _name = 'beesdoo.shift.subscribe.shift.exchange'
    _description = 'Subscribe Exchange shift'

    @api.onchange('worker_id')
    def onchange_exchanged_timeslot(self):
        # TODO : prendre en compte qd il est inscris a aucun shift
        for record in self:
            if not record.worker_id:
                record.exchanged_timeslot_id = False
            else:
                timeslots = self.env["beesdoo.shift.template.dated"].my_timeslot(record.worker_id)
                # record.available_timeslots = timeslots
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in timeslots:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create({
                        'template_id': template.id,
                        'date': date,
                        'store': False,
                    })
                return {
                    'domain': {'exchanged_timeslot_id': [('id', 'in', temp.ids)]}
                }

    worker_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env["res.partner"].browse(
            self._context.get("active_id")
        ),
        required=True,
        string="Cooperator",
    )

    exchanged_timeslot_id = fields.Many2one('beesdoo.shift.template.dated', string='exchanged_timeslot')

    @api.onchange('exchanged_timeslot_id')
    def _get_available_timeslot(self):
        for record in self:
            if not record.exchanged_timeslot_id:
                record.confirmed_timeslot_id = False
            else:
                timeslots = all_timeslot = self.env["beesdoo.shift.template.dated"].display_timeslot(record.exchanged_timeslot_id)
                # record.available_timeslots = timeslots
                temp = self.env["beesdoo.shift.template.dated"]
                for rec in timeslots:
                    template = rec.template_id
                    date = rec.date
                    temp |= temp.create({
                        'template_id': template.id,
                        'date': date,
                        'store': False,
                    })
                return {
                    'domain': {'asked_timeslot_ids': [('id', 'in', temp.ids)]}
                }
    # TODO : relational fields
    asked_timeslot_ids = fields.Many2many(
        comodel_name='beesdoo.shift.template.dated',
        #inverse_name='id',
        relation='exchange_template_dated',
        string='asked_timeslots',
    )
    request_date = fields.Date(required=True, string='date')