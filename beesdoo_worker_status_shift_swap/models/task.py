# import json

from odoo import models


class Task(models.Model):
    _inherit = "beesdoo.shift.shift"

    def _get_counter_date_state_change(self, new_state):
        data, status = super(Task, self)._get_counter_date_state_change(new_state)

        if (
            self.worker_id.working_mode == "irregular"
            and new_state in ["done", "absent_0"]
            and self.solidarity_offer_ids[0]
        ):
            data["sr"] = 0
            # old_data = json.loads(self.revert_info)
            # data["irregular_absence_date"] = old_data["data"]
            #    .get("irregular_absence_date", False)
            # data["irregular_absence_counter"] = old_data["data"]
            #    .get("irregular_absence_counter", 0)

        return data, status
