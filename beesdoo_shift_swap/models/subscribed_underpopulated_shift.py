from datetime import datetime, timedelta

from odoo import _, api, fields, models

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        return start_date + timedelta(n)


class SubscribeUnderpopulatedShift(models.Model):
    _name = "beesdoo.shift.subscribed_underpopulated_shift"

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
    exchanged_timeslot_id = fields.Many2one("beesdoo.shift.template.dated")
    exchange_status = fields.Boolean(
        default=False, string="Status Exchange Shift"
    )
    exchanged_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_exchanged_already_generated"
    )
    confirmed_timeslot_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="asked_shift"
    )
    confirmed_shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_comfirmed_already_generated"
    )
    confirme_status = fields.Boolean(
        default=False, string="status comfirme shift"
    )
    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    @api.depends("exchanged_timeslot_id")
    def _compute_exchanged_already_generated(self):
        for record in self:
            # if the supercooperateur make the exchange
            current_worker = self.worker_id

            if not record.exchanged_timeslot_id:
                record.exchanged_shift_id = False

            elif self.exchange_status:
                record.exchanged_shift_id = False
            # check if the new_shift is already generated
            else:
                # Get the shift if it is already generated
                subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", "=", record.exchanged_timeslot_id.date),
                        ("worker_id", "=", current_worker.id),
                        (
                            "task_template_id",
                            "=",
                            record.exchanged_timeslot_id.template_id.id,
                        ),
                    ],
                    limit=1,
                )

                # check if is there a shift generated
                if subscribed_shifts_rec:
                    record.exchanged_shift_id = subscribed_shifts_rec
                    return True
                return False

    @api.depends("confirmed_timeslot_id")
    def _compute_comfirmed_already_generated(self):
        for record in self:
            # Get current date
            now = datetime.now()
            if not record.confirmed_timeslot_id:
                record.confirmed_shift_id = False
            elif self.confirme_status:
                record.confirmed_shift_id = False
            else:
                # Get the shift if it is already generated
                future_subscribed_shifts_rec = self.env[
                    "beesdoo.shift.shift"
                ].search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("start_time", "=", record.exchanged_timeslot_id.date),
                        (
                            "task_template_id",
                            "=",
                            record.exchanged_timeslot_id.template_id.id,
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

    def update_status(self):
        if (
            self.exchanged_timeslot_id
            and self.confirmed_timeslot_id
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
            if not self.exchanged_shift_id.worker_id and self.confirme_status:
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
            subscribed_shift_rec.write({"worker_id": self.worker_id})

            # Subscribe done, change the status
            self.confirme_status = 1

            # update status
            self.update_status()
            if (
                not self.exchanged_shift_id.worker_id
                and not self.confirme_status
            ):
                return False
            return True
        return True

    def get_underpopulated_shift(self, my_timeslot):
        available_timeslot = self.env["beesdoo.shift.template.dated"]
        timeslots = self.env["beesdoo.shift.template.dated"].display_timeslot(
            my_timeslot
        )
        exchange = self.env[
            "beesdoo.shift.subscribed_underpopulated_shift"
        ].search([])

        for timeslot in timeslots:
            nb_workers_change = 0
            for ex in exchange:

                if (
                    ex.exchanged_timeslot_id.template_id
                    == timeslot.template_id
                    and ex.exchanged_timeslot_id.date == timeslot.date
                ):
                    # Enlever un worker
                    nb_workers_change -= 1
                if (
                    ex.confirmed_timeslot_id.template_id
                    == timeslot.template_id
                    and ex.confirmed_timeslot_id.date == timeslot.date
                ):
                    # ajouter un worker
                    nb_workers_change += 1
            nb_worker_wanted = timeslot.template_id.worker_nb
            nb_worker_present = (
                nb_worker_wanted - timeslot.template_id.remaining_worker
            ) + nb_workers_change
            percentage_presence = (nb_worker_present / nb_worker_wanted) * 100
            min_percentage_presence = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.percentage_presence")
            )
            if percentage_presence <= min_percentage_presence:
                available_timeslot |= timeslot

        return available_timeslot