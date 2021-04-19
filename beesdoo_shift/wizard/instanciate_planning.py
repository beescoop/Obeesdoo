from odoo import _, api, fields, models


class InstanciatePlanning(models.TransientModel):
    _name = "beesddoo.shift.generate_planning"
    _description = "beesddoo.shift.generate_planning"

    def _get_planning(self):
        return self._context.get("active_id")

    date_start = fields.Date(
        "First Day of planning (should be monday)", required=True
    )
    planning_id = fields.Many2one(
        "beesdoo.shift.planning", readonly=True, default=_get_planning
    )

    @api.multi
    def generate_task(self):
        self.ensure_one()
        self = self.with_context(
            visualize_date=self.date_start, tracking_disable=True
        )
        shifts = self.planning_id.task_template_ids._generate_task_day()
        for rec in shifts :
            data = {
                "name": rec.name,
                "task_template_id": rec.task_template_id.id,
                "task_type_id": rec.task_type_id.id,
                "super_coop_id": rec.super_coop_id.id,
                "worker_id": rec.worker_id.id,
                "is_regular": rec.is_regular,
                "start_time": rec.start_time,
                "end_time": rec.end_time,
                "state": "open",
            }
            shifts |= rec.create(data)

        return {
            "name": _("Generated Shift"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "kanban,calendar,tree,form,pivot",
            "res_model": "beesdoo.shift.shift",
            "target": "current",
            "domain": [("id", "in", shifts.ids)],
            "context": {"search_default_gb_day": 1},
        }
