# import json

from odoo import models


class Task(models.Model):
    _inherit = "beesdoo.shift.shift"

    def _get_counter_date_state_change(self, new_state):
        data, status = super(Task, self)._get_counter_date_state_change(new_state)

        if (
            self.worker_id.working_mode == "irregular"
            and new_state in ["done", "absent_0"]
            and self.is_solidarity
        ):
            # Set status to None to prevent counter update on solidarity shift
            status = None

        return data, status
