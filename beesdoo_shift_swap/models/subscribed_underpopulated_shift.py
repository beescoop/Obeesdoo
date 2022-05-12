from datetime import datetime, timedelta

from odoo import fields, models


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        return start_date + timedelta(n)


class SubscribeUnderpopulatedShift(models.Model):
    _name = "beesdoo.shift.subscribed_underpopulated_shift"
    _description = "A model to track an exchange with an underpopulated shift"

    def _get_selection_status(self):
        return [("draft", "Draft"), ("validate", "Validate"), ("done", "Done")]

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
    exchanged_shift_id = fields.Many2one("beesdoo.shift.shift")

    confirmed_tmpl_dated_id = fields.Many2one("beesdoo.shift.template.dated")
    confirmed_shift_id = fields.Many2one("beesdoo.shift.shift")

    # True if worker has been unsubscribed from exchanged_shift
    exchange_status = fields.Boolean(default=False, string="Status Exchange Shift")

    # True if worker has been subscribed to confirmed_shift
    confirme_status = fields.Boolean(default=False, string="status comfirme shift")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    def create(self, vals_list):
        """
        Override create() method to unsubscribe the worker
        to the old shift and subscribe him/her to the new one
        """
        res = super(SubscribeUnderpopulatedShift, self).create(vals_list)
        res._unsubscribe_old_shift_if_generated()
        res._subscribe_new_shift_if_generated()
        return res

    def _unsubscribe_old_shift_if_generated(self):
        if self.exchanged_tmpl_dated_id and not self.exchanged_shift_id:
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
                        "is_compensation": False,
                    }
                )
                self.exchanged_shift_id = exchanged_shift
                self.exchange_status = True
                if self.confirme_status:
                    self.state = "done"
                return True
        return False

    def _subscribe_new_shift_if_generated(self):
        if self.confirmed_tmpl_dated_id and not self.confirmed_shift_id:
            wanted_shift = self.env["beesdoo.shift.shift"].search(
                [
                    ("start_time", "=", self.confirmed_tmpl_dated_id.date),
                    (
                        "task_template_id",
                        "=",
                        self.confirmed_tmpl_dated_id.template_id.id,
                    ),
                    ("worker_id", "=", None),
                ],
                limit=1,
            )
            if wanted_shift:
                is_compensation = False
                if self.exchanged_shift_id and self.exchanged_shift_id.is_compensation:
                    is_compensation = True
                wanted_shift.write(
                    {
                        "worker_id": self.worker_id.id,
                        "is_regular": False if is_compensation else True,
                        "is_compensation": True if is_compensation else False,
                    }
                )
                self.confirmed_shift_id = wanted_shift
                self.confirme_status = True
                if self.exchange_status:
                    self.state = "done"
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
