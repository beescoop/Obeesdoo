from odoo import fields, models


class SolidarityShiftRequest(models.Model):
    _inherit = "beesdoo.shift.solidarity.request"

    def _get_personal_counter_status(self):
        return [
            ("not_modified", "Not modified"),
            ("request_ok", "Request OK"),
            ("cancel_ok", "Cancel OK"),
        ]

    personal_counter_status = fields.Selection(
        selection=_get_personal_counter_status, default="not_modified"
    )

    def update_personal_counter(self):
        worker = self.worker_id
        if worker:
            if worker.working_mode == "irregular":
                if (
                    self.state == "validated"
                    and self.personal_counter_status == "not_modified"
                ):
                    worker.cooperative_status_ids[0].sr += 1
                    self.personal_counter_status = "request_ok"
                elif (
                    self.state == "cancelled"
                    and self.personal_counter_status == "request_ok"
                ):
                    worker.cooperative_status_ids[0].sr -= 1
                    self.personal_counter_status = "cancel_ok"
            return True
        return False
