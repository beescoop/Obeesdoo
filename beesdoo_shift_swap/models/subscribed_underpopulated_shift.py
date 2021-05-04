from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import Warning

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)) :
        return start_date + timedelta(n)


class SubscribeUnderpopulatedShift(models.Model):
    _name = 'beesdoo.shift.subscribed_underpopulated_shift'


    def _get_selection_status(self):
        return [
            ('draft','Draft'),
            ('validate','Validate'),
            ('done','Done')
        ]

    state=fields.Selection(
        selection=_get_selection_status,
        default='draft'
    )
    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
    )

    exchanged_timeslot_id = fields.Many2one(
        "beesdoo.shift.template.dated"
    )
    exchange_status = fields.Boolean(default=False, string="Status Exchange Shift")
    exchanged_shift_id = fields.One2many(
        comodel_name='beesdoo.shift.shift',
        inverse_name='id',
        compute='_compute_exchanged_already_generated'
    )

    confirmed_timeslot_id = fields.Many2one(
        "beesdoo.shift.template.dated",
        string="asked_shift"
    )
    confirmed_shift_id = fields.One2many(
        comodel_name='beesdoo.shift.shift',
        inverse_name='id',
        compute='_compute_comfirmed_already_generated'
    )
    confirme_status = fields.Boolean(default=False, string="status comfirme shift")
    date = fields.Date(required=True,default=datetime.date(datetime.now()))


    def update_status(self):
        if self.exchanged_timeslot_id and self.confirmed_timeslot_id and self.worker_id and self.date:
            self.write({"state" : "validate"})
            if self.exchange_status and self.confirme_status :
                self.write({"state" : "done"})

    @api.multi
    def _compute_exchanged_already_generated(self):

        #if the supercooperateur make the exchange
        current_worker = self.worker_id

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
                        ('start_time', '=', self.exchanged_timeslot_id.date),
                        ("worker_id", "=", current_worker.id),
                        ("task_template_id", "=", self.exchanged_timeslot_id.template_id.id)
                    ],
                    limit=1,
                )
            )

            # check if is there a shift generated
            if subscribed_shifts_rec:
                self.exchanged_shift_id = subscribed_shifts_rec
                return True
            return False
        return True

    @api.multi
    def button_check_shift_exchanged(self):
        for exchange in self :
            if not exchange.exchanged_timeslot_id :
                raise Warning('Please provide an exchange timeslot')
            if exchange.exchanged_timeslot_id and not exchange._compute_exchanged_already_generated() :
                raise Warning('The shift has not been generated')
        return True

    @api.multi
    def _compute_comfirmed_already_generated(self):

        # Get current date
        now = datetime.now()

        if not self.confirmed_shift_id:
            # Get the shift if it is already generated
            future_subscribed_shifts_rec = (
                self.env["beesdoo.shift.shift"]
                    .search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ('start_time','=',self.exchanged_timeslot_id.date),
                        ("task_template_id", "=", self.exchanged_timeslot_id.template_id.id),
                        ("worker_id","=",None),
                    ],
                    limit=1,
                )
            )
            # check if is there a shift generated
            if future_subscribed_shifts_rec:
                self.confirmed_shift_id = future_subscribed_shifts_rec
                return True
            return False
        return True

    @api.multi
    def button_check_shift_comfirmed(self):
        for exchange in self:
            if not exchange.confirmed_timeslot_id:
                raise Warning('Please provide an exchange timeslot')
            if exchange.confirmed_timeslot_id and not exchange._compute_comfirmed_already_generated():
                raise Warning('The shift has not been generated')
        return True


    @api.multi
    def unsubscribe_shift(self):
        unsubscribed_shifts_rec =  self.exchanged_shift_id
        unsubscribed_shifts_rec.write({
           "worker_id" : False
        })
        self.confirme_status = 1
        self.update_status()
        if not self.exchanged_shift_id.worker_id and self.confirme_status:
            return True
        return False

    @api.multi
    def button_unsubscribe(self):
        for exchange in self:
            if not exchange.exchanged_shift_id:
                raise Warning('Shift not generated')
            if not exchange.unsubscribe_shift():
                raise Warning('cannot unsubscribe')
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
        # Get the wanted shift
        subscribed_shift_rec = self.confirmed_shift_id

        subscribed_shift_rec.is_regular = True

        # Get the user
        subscribed_shift_rec.worker_id = self.worker_id

        # Subscribe done, change the status
        self.exchange_status = 1

        #update status
        self.update_status()
        if not self.exchanged_shift_id.worker_id and not self.exchange_status:
            return False
        return True

    @api.multi
    def button_subscribe_shift(self):
        for exchange in self:
            if not exchange.confirmed_shift_id:
                raise Warning('Shift not generated')
            if not exchange.subscribe_shift():
                raise Warning('cannot unsubscribe')
        return True


    def display_underpopulated_shift(self,my_timeslot):
        available_timeslot = self.env["beesdoo.shift.template.dated"]
        timeslots = self.env["beesdoo.shift.template.dated"].display_timeslot(my_timeslot)
        exchange = self.env["beesdoo.shift.subscribed_underpopulated_shift"].search([])

        for timeslot in timeslots :
            nb_workers_change = 0
            for ex in exchange :

                if ex.exchanged_timeslot_id.template_id == timeslot.template_id and ex.exchanged_timeslot_id.date == timeslot.date:
                    #Enlever un worker
                    nb_workers_change -= 1
                if ex.confirmed_timeslot_id.template_id == timeslot.template_id and ex.confirmed_timeslot_id.date == timeslot.date:
                    # ajouter un worker
                    nb_workers_change += 1
            nb_worker_wanted = timeslot.template_id.worker_nb
            nb_worker_present = (nb_worker_wanted - timeslot.template_id.remaining_worker) + nb_workers_change
            percentage_presence = (nb_worker_present/nb_worker_wanted) * 100
            if percentage_presence <= 20 :
                available_timeslot |= timeslot

        return available_timeslot