from odoo import fields, models


class Task(models.Model):
    _inherit = "beesdoo.shift.shift"

    @api.constrains("worker_id")
    def _check_worker_id(self):
        """
        When worker_id changes we need to check whether is_regular
        and is_compensation are set correctly.
        When worker_id is set to a worker that doesn't need field
        is_regular and is_compensation, these two fields are set to
        False.
        """
        for task in self:
            if task.working_mode == "regular":
                self._compensation_validation(task)
            else:
                task.write({"is_regular": False, "is_compensation": False})
            if task.worker_id:
                if task.worker_id == task.replaced_id:
                    raise UserError(_("A worker cannot replace himself."))

    def _compensation_validation(self, task):
        """
        Raise a validation error if the fields is_regular and
        is_compensation are not properly set.
        """
        if task.is_regular == task.is_compensation or not (
            task.is_regular or task.is_compensation
        ):
            raise ValidationError(
                _(
                    "You must choose between Regular Shift or "
                    "Compensation Shift."
                )
            )

    @api.constrains("is_regular", "is_compensation")
    def _check_compensation(self):
        for task in self:
            if task.working_mode == "regular":
                self._compensation_validation(task)


    #################################
    #       State Definition        #
    #################################

    def _get_selection_status(self):
        return [
            ("open", "Confirmed"),
            ("done", "Attended"),
            ("absent_2", "Absent - 2 compensations"),
            ("absent_1", "Absent - 1 compensation"),
            ("absent_0", "Absent - 0 compensation"),
            ("cancel", "Cancelled"),
        ]

    def _get_color_mapping(self, state):
        return {
            "draft": 0,
            "open": 1,
            "done": 5,
            "absent_2": 2,
            "absent_1": 7,
            "absent_0": 3,
            "cancel": 9,
        }[state]

    def _get_final_state(self):
        return ["done", "absent_2", "absent_1", "absent_0"]

    state = fields.Selection(selection=_get_selection_status)

    ##############################################
    #    Change counter when state change        #
    ##############################################
    def _get_counter_date_state_change(self, new_state):
        data = {}
        if self.worker_id.working_mode == "regular":

            if not self.replaced_id:  # No replacement case
                status = self.worker_id.cooperative_status_ids[0]
            else:
                status = self.replaced_id.cooperative_status_ids[0]

            if new_state == "done" and not self.is_regular:
                # Regular counter is always updated first
                if status.sr < 0:
                    data["sr"] = 1
                elif status.sc < 0:
                    data["sc"] = 1
                # Bonus shift case
                else:
                    data["sr"] = 1

            if new_state == "absent_2":
                data["sr"] = -1
                data["sc"] = -1

            if new_state == "absent_1":
                data["sr"] = -1

        elif self.worker_id.working_mode == "irregular":
            status = self.worker_id.cooperative_status_ids[0]
            if new_state == "done" or new_state == "absent_0":
                data["sr"] = 1
                data["irregular_absence_date"] = False
                data["irregular_absence_counter"] = (
                    1 if status.irregular_absence_counter < 0 else 0
                )
            if new_state == "absent_2" or new_state == "absent_1":
                if new_state == "absent_2":
                    data["sr"] = -1
                data["irregular_absence_date"] = self.start_time.date()
                data["irregular_absence_counter"] = -1
        return data, status
