from datetime import datetime, timedelta

from odoo import api, fields, models


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
    exchanged_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_exchanged_already_generated"
    )

    confirmed_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="asked_shift"
    )
    confirmed_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_comfirmed_already_generated"
    )

    # True if worker has been unsubscribed from exchanged_shift
    exchange_status = fields.Boolean(default=False, string="Status Exchange Shift")

    # True if worker has been subscribed to confirmed_shift
    confirme_status = fields.Boolean(default=False, string="status comfirme shift")

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    @api.depends("exchanged_tmpl_dated_id")
    def _compute_exchanged_already_generated(self):
        for rec in self:
            if not rec.exchanged_tmpl_dated_id:
                rec.exchanged_shift_id = False
            elif self.exchange_status:
                rec.exchanged_shift_id = False
            # check if the new_shift is already generated
            else:
                # Get the shift if it is already generated
                subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", "=", rec.exchanged_tmpl_dated_id.date),
                        ("worker_id", "=", rec.worker_id.id),
                        (
                            "task_template_id",
                            "=",
                            rec.exchanged_tmpl_dated_id.template_id.id,
                        ),
                    ],
                    limit=1,
                )

                # check if is there a shift generated
                if subscribed_shifts_rec:
                    rec.exchanged_shift_id = subscribed_shifts_rec
                    return True
                return False

    @api.depends("confirmed_tmpl_dated_id")
    def _compute_comfirmed_already_generated(self):
        for record in self:
            # Get current date
            now = datetime.now()
            if not record.confirmed_tmpl_dated_id:
                record.confirmed_shift_id = False
            elif self.confirme_status:
                record.confirmed_shift_id = False
            else:
                # Get the shift if it is already generated
                future_subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("start_time", "=", record.confirmed_tmpl_dated_id.date),
                        (
                            "task_template_id",
                            "=",
                            record.confirmed_tmpl_dated_id.template_id.id,
                        ),
                        ("worker_id", "=", None),
                    ],
                    limit=1,
                )
                # Check if there is a shift generated
                if future_subscribed_shifts_rec:
                    record.confirmed_shift_id = future_subscribed_shifts_rec
                    return True
                return False

    def update_status(self):
        if (
            self.exchanged_tmpl_dated_id
            and self.confirmed_tmpl_dated_id
            and self.worker_id
            and self.date
        ):
            self.write({"state": "validate"})
            if self.exchange_status and self.confirme_status:
                self.write({"state": "done"})

    @api.multi
    def unsubscribe_shift(self):
        if not self.exchange_status:
            unsubscribed_shifts_rec = self.exchanged_shift_id
            unsubscribed_shifts_rec.write({"worker_id": False})
            self.exchange_status = True
            self.update_status()
            if not self.exchanged_shift_id.worker_id and self.exchange_status:
                return True
            return False
        return True

    @api.multi
    def subscribe_shift(self):
        """
        Subscribe the user into the given shift
        this is done only if :
            *the user can subscribe
            *the given shift exist
            *the shift status is open
            *the user hasn't done another exchange 2month before
        :return:
        """
        if not self.confirme_status:
            if not self.confirmed_shift_id:
                return False
            # Get the wanted shift
            subscribed_shift_rec = self.confirmed_shift_id
            # Subscribe the worker
            subscribed_shift_rec.write(
                {"worker_id": self.worker_id.id, "is_regular": True}
            )
            # Change the status
            self.confirme_status = True
            # Update status
            self.update_status()
            if not self.exchanged_shift_id.worker_id and not self.confirme_status:
                return False
        return True

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
