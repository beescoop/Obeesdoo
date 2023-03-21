from odoo import _, fields, models


class InstantiatePlanning(models.TransientModel):
    _name = "shift.generate_planning"
    _description = "shift.generate_planning"

    def _get_planning(self):
        return self._context.get("active_id")

    date_start = fields.Date("First Day of planning (should be Monday)", required=True)
    planning_id = fields.Many2one(
        "shift.planning", readonly=True, default=_get_planning
    )

    def generate_task(self):
        self.ensure_one()
        self = self.with_context(visualize_date=self.date_start, tracking_disable=True)
        shifts = self.planning_id.task_template_ids.generate_task_day()
        return {
            "name": _("Generated Shift"),
            "type": "ir.actions.act_window",
            "view_mode": "kanban,calendar,tree,form,pivot",
            "res_model": "shift.shift",
            "target": "current",
            "domain": [("id", "in", shifts.ids)],
            "context": {"search_default_gb_day": 1},
        }
