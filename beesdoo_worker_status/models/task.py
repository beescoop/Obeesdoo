from odoo import fields, models


class Task(models.Model):
    _inherit = "beesdoo.shift.shift"

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
        """
        Set of colors:
            0: none,
            1: dark orange,
            2: orange,
            3: yellow,
            4: light blue,
            5: dark purple,
            6: light red (pink),
            7: cyan,
            8: dark blue,
            9: magenta (red),
            10: green,
            11: purple
        """
        return {
            "open": 0,
            "done": 10,
            "absent_2": 9,
            "absent_1": 2,
            "absent_0": 3,
            "cancel": 5,
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
