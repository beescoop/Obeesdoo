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
    exchange_status = fields.Boolean(default=False, string="Status Exchange Shift")

    @api.depends("exchanged_tmpl_dated_id")
    def _compute_exchanged_already_generated(self):
        for record in self:
            # if the supercooperateur make the exchange
            current_worker = self.worker_id

            if not record.exchanged_tmpl_dated_id:
                record.exchanged_shift_id = False

            elif self.exchange_status:
                record.exchanged_shift_id = False
            # check if the new_shift is already generated
            else:
                # Get the shift if it is already generated
                subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", "=", record.exchanged_tmpl_dated_id.date),
                        ("worker_id", "=", current_worker.id),
                        (
                            "task_template_id",
                            "=",
                            record.exchanged_tmpl_dated_id.template_id.id,
                        ),
                    ],
                    limit=1,
                )

                # check if is there a shift generated
                if subscribed_shifts_rec:
                    record.exchanged_shift_id = subscribed_shifts_rec
                    return True
                return False

    exchanged_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_exchanged_already_generated"
    )

    confirmed_tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="asked_shift"
    )

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
                # check if is there a shift generated
                if future_subscribed_shifts_rec:
                    record.confirmed_shift_id = future_subscribed_shifts_rec
                    return True
                return False

    confirmed_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_comfirmed_already_generated"
    )
    confirme_status = fields.Boolean(default=False, string="status comfirme shift")
    date = fields.Date(required=True, default=datetime.date(datetime.now()))

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
            self.exchange_status = 1
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
            # Get the wanted shift
            subscribed_shift_rec = self.confirmed_shift_id
            subscribed_shift_rec.is_regular = True
            # Get the user
            subscribed_shift_rec.write({"worker_id": self.worker_id.id})

            # Subscribe done, change the status
            self.confirme_status = 1

            # update status
            self.update_status()
            if not self.exchanged_shift_id.worker_id and not self.confirme_status:
                return False
            return True
        return True

    def get_underpopulated_shift(self, sort_date_desc=False):
        available_tmpl_dated = self.env["beesdoo.shift.template.dated"]
        tmpl_dated = self.env["beesdoo.shift.template.dated"].display_tmpl_dated()
        exchange = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search([])
        for template in tmpl_dated:
            nb_workers_change = 0
            for ex in exchange:

                if (
                    ex.exchanged_tmpl_dated_id.template_id == template.template_id
                    and ex.exchanged_tmpl_dated_id.date == template.date
                ):
                    # Enlever un worker
                    nb_workers_change -= 1
                if (
                    ex.confirmed_tmpl_dated_id.template_id == template.template_id
                    and ex.confirmed_tmpl_dated_id.date == template.date
                ):
                    # ajouter un worker
                    nb_workers_change += 1
            nb_worker_wanted = template.template_id.worker_nb
            nb_worker_present = (
                nb_worker_wanted - template.template_id.remaining_worker
            ) + nb_workers_change
            percentage_presence = (nb_worker_present / nb_worker_wanted) * 100
            min_percentage_presence = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.percentage_presence")
            )
            if percentage_presence <= min_percentage_presence:
                available_tmpl_dated |= template

        if sort_date_desc:
            available_tmpl_dated = available_tmpl_dated.sorted(key=lambda r: r.date)

        return available_tmpl_dated
