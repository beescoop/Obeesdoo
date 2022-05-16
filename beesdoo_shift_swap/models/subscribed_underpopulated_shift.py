from datetime import datetime

from odoo import fields, models


class SubscribeUnderpopulatedShift(models.Model):
    _name = "beesdoo.shift.subscribed_underpopulated_shift"
    _description = "A model to track an exchange with an underpopulated shift"

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

    exchanged_tmpl_dated_id = fields.Many2one("beesdoo.shift.template.dated")
    is_exchanged_shift_compensation = fields.Boolean(default=False)

    wanted_tmpl_dated_id = fields.Many2one("beesdoo.shift.template.dated")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        to the old shift and subscribe him/her to the new one
        """
        res = super(SubscribeUnderpopulatedShift, self).create(vals_list)
        res._unsubscribe_old_shift_if_generated()
        res._subscribe_new_shift_if_generated()
        res.state = "validated"
        return res

    def _unsubscribe_old_shift_if_generated(self):
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
                self.is_exchanged_shift_compensation = exchanged_shift.is_compensation
                exchanged_shift.write(
                    {
                        "worker_id": False,
                        "is_regular": False,
                        "is_compensation": False,
                    }
                )
                return True
        return False

    def _subscribe_new_shift_if_generated(self):
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
                        "is_regular": False
                        if self.is_exchanged_shift_compensation
                        else True,
                        "is_compensation": True
                        if self.is_exchanged_shift_compensation
                        else False,
                    }
                )
                return True
        return False

    def get_underpopulated_shift(self, sort_date_desc=False):
        available_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        tmpl_dated = self.env["beesdoo.shift.template.dated"].get_next_tmpl_dated()
        min_percentage_presence = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.percentage_presence")
        )
        for template in tmpl_dated:
            nb_worker_wanted = template.template_id.worker_nb
            nb_worker_present = nb_worker_wanted - template.template_id.remaining_worker
            percentage_presence = (nb_worker_present / nb_worker_wanted) * 100
            if percentage_presence <= min_percentage_presence:
                available_tmpl_dated |= template

        if sort_date_desc:
            available_tmpl_dated = available_tmpl_dated.sorted(key=lambda r: r.date)

        return available_tmpl_dated
