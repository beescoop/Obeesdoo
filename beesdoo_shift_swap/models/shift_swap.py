from odoo import fields, models


class ShiftSwap(models.Model):
    _name = "beesdoo.shift.swap"
    _inherit = ["beesdoo.shift.swap.mixin"]
    _description = "A model to track an exchange with an empty shift"

    def _get_selection_status(self):
        return [("draft", "Draft"), ("validated", "Validated")]

    state = fields.Selection(selection=_get_selection_status, default="draft")

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    exchanged_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Exchanged shift"
    )

    wanted_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="New shift"
    )

    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        to the old shift and subscribe him/her to the new one
        """
        res = super(ShiftSwap, self).create(vals_list)
        res._unsubscribe_old_shift_if_generated()
        res._subscribe_new_shift_if_generated()
        res.state = "validated"
        return res

    def _unsubscribe_old_shift_if_generated(self):
        """
        Unsubscribe self.worker_id to the shift matching
        exchanged_tmpl_dated_id if it is generated.
        Return True is unsubscription is successful.
        :return: Boolean
        """
        if self.exchanged_tmpl_dated_id:
            exchanged_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.exchanged_tmpl_dated_id.date),
                    ("worker_id", "=", self.worker_id.id),
                    (
                        "task_template_id",
                        "=",
                        self.exchanged_tmpl_dated_id.template_id.id,
                    ),
                ],
                limit=1,
            )
            if exchanged_shift:
                exchanged_shift.write(
                    {
                        "worker_id": False,
                        "is_regular": False,
                    }
                )
                return True
        return False

    def _subscribe_new_shift_if_generated(self):
        """
        Subscribe self.worker_id to the shift matching
        wanted_tmpl_dated_id if it is generated.
        Return True is subscription is successful.
        :return: Boolean
        """
        if self.wanted_tmpl_dated_id:
            wanted_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.wanted_tmpl_dated_id.date),
                    (
                        "task_template_id",
                        "=",
                        self.wanted_tmpl_dated_id.template_id.id,
                    ),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if wanted_shift:
                wanted_shift.write(
                    {
                        "worker_id": self.worker_id.id,
                        "is_regular": True,
                    }
                )
                return True
        return False

    def update_shift_data(self, shift, swap_subscription_done):
        if (
            not shift["worker_id"]
            and self.wanted_tmpl_dated_id.template_id.id == shift["task_template_id"]
            and shift["start_time"] == self.wanted_tmpl_dated_id.date
            and self.id not in swap_subscription_done
        ):
            shift["worker_id"] = self.worker_id.id
            shift["is_regular"] = True
            swap_subscription_done.append(self.id)
        if (
            self.worker_id.id == shift["worker_id"]
            and shift["task_template_id"] == self.exchanged_tmpl_dated_id.template_id.id
            and shift["start_time"] == self.exchanged_tmpl_dated_id.date
        ):
            shift["worker_id"] = False
            shift["is_regular"] = False
        return shift, swap_subscription_done, False
