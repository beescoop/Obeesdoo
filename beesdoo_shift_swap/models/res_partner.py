from odoo import _, api, models
from datetime import timedelta



class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.multi
    def coop_swap(self):
        return {
            "name": _("Subscribe Swap Cooperator"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "beesdoo.shift.subscribe.shift.swap",
            "target": "new",
        }

    @api.multi
    def my_next_shift(self):
        shifts = super(ResPartner,self).my_next_shift()
        exchanges = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search([])
        worker_id = self.id
        for shift in shifts:
            for exchange in exchanges:
                if exchange.worker_id.id == worker_id and shift.task_template_id == exchange.exchanged_timeslot_id.template_id and shift.start_time == exchange.exchanged_timeslot_id.date:
                    updated_data = {
                        "task_template_id" : exchange.confirmed_timeslot_id.template_id,
                        "task_type_id": exchange.confirmed_timeslot_id.template_id.task_type_id.id,
                        "super_coop_id": exchange.confirmed_timeslot_id.template_id.super_coop_id.id,
                        "worker_id": worker_id,
                        "start_time": exchange.confirmed_timeslot_id.date,
                        "end_time": exchange.confirmed_timeslot_id.date + timedelta(hours=exchange.confirmed_timeslot_id.template_id.duration)
                    }
                    shift.update(updated_data)
        return shifts
