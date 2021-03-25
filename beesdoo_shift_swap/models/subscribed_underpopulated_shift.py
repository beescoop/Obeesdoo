from odoo import models, fields, api
from datetime import datetime


class subscribe_underpopulated_shift(models.Model):
    _name = 'beesdoo.shift.subscribed_underpopulated_shift'

    exchanged_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='exchanged_shift'
    )
    exchanged_shift_id = fields.One2many(
        comodel_name='beesdoo.shift.shift',
        inverse_name='id',
        compute='is_shift_exchanged_already_generated'
    )
    comfirmed_timeslot_id = fields.One2many(
        comodel_name='beesdoo.shift.timeslots_date',
        inverse_name='id',
        string='asked_shift'
    )
    comfirmed_shift_id = fields.One2many(
        comodel_name='beesdoo.shift.shift',
        inverse_name='id',
        compute='is_shift_comfirmed_already_generated'
    )

    date = fields.Datetime(required=True)
    status_generated_and_subscribed = fields.Char(compute='compute_status')

    def is_shift_exchanged_already_generated(self):
        # Get current user
        cur_user = self.env["res.users"].browse(self.uid)

        # Get current date
        now = datetime.now()

        # check if the old_shift is already generated
        # check if the new_shift is already generated
        if not self.exchanged_shift_id:
            # Get the shift if it is already generated
            subscribed_shifts_rec = (
                self.env["beesdoo.shift.shift"]
                    .search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("worker_id", "=", cur_user.partner_id.id),
                        ("task_template_id", "=", self.exchanged_timeslot_id.template_id)
                    ],
                )
            )

            # check if is there a shift generated
            if subscribed_shifts_rec:
                self.exchanged_shift_id == subscribed_shifts_rec
                return 1
            return 0
        return 1

    def is_shift_comfirmed_already_generated(self):
        # Get current user
        cur_user = self.env["res.users"].browse(self.uid)

        # Get current date
        now = datetime.now()

        if not self.comfirmed_shift_id:
            # Get the shift if it is already generated
            future_subscribed_shifts_rec = (
                self.env["beesdoo.shift.shift"]
                    .search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("task_template_id", "=", self.exchanged_timeslot_id.template_id)
                    ],
                    order="start_time, task_template_id, task_type_id",
                )
            )

            # check if is there a shift generated
            if future_subscribed_shifts_rec:
                self.comfirmed_shift_id == future_subscribed_shifts_rec
                return 1
            return 0
        return 1

    def compute_status(self):
        if self.is_shift_exchanged_already_generated() and self.is_shift_comfirmed_already_generated():
            return 3
        if not self.is_shift_exchanged_already_generated() and self.is_shift_comfirmed_already_generated():
            return 2
        if self.is_shift_exchanged_already_generated() and not self.is_shift_comfirmed_already_generated():
            return 1
        if not self.is_shift_exchanged_already_generated() and not self.is_shift_comfirmed_already_generated():
            return 0


    def make_the_exchange(self, exchange_id=-1, **kw):
        """
        Subscribe the current connected user into the given shift
        This is done only if :
            * shift sign up is authorised via configuration panel
            * the user can subscribe
            * the given exchange exist
            * the shift status is open
            * the shift is free for subscription
            * the shift is starting after the time interval
            for attendance sheet generation defined in beesdoo_shift settings
        """
        # Get current user
        cur_user = self.env["res.users"].browse(self.uid)
        # Get the exchange
        exchange = self.env["subscribe_underpopulated_shift"].sudo().brows(exchange_id)
        start_time_limit = datetime.now()

        if exchange:
            if exchange.comfirmed_shift_id :
                comfirmed_shift = self.env["beesdoo.shift.shift"].browse(exchange.comfirmed_shift_id)
                if comfirmed_shift.state == "open" and comfirmed_shift.start_time > start_time_limit and not comfirmed_shift.worker_id :
                    comfirmed_shift.worker_id = cur_user.partner_id
            if exchange.exchanged_shift_id:
                exchanged_shift = self.env["beesdoo.shift.shift"].browse(exchange.exchanged_shift_id)
                if exchanged_shift.state == "close" and exchanged_shift.start_time > start_time_limit and exchanged_shift.worker_id == cur_user.partner_id :
                    exchanged_shift.worker_id = None



'''
    def register_exchange(self):
        #we recover the data previously stored in session
        old_timeslot = request.session['exchanged_timeslot']
        new_timeslot = request.session['comfirmed_timeslot']
        date = str(datetime.now())

        #we create a new object
        exchange = self.env["beesdoo.shift.subscribed_underpopulated_shift"].sudo().create({
                "exchanged_timeslot_id" : old_timeslot,
                "comfirmed_timeslot_id" : new_timeslot,
                "date" : date
            })
        exchange.subscribe_the_exchange()
        return exchange
'''
