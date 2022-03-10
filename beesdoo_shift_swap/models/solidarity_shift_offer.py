from datetime import datetime

from odoo import api, fields, models


class SolidarityShiftOffer(models.Model):
    _name = "beesdoo.shift.solidarity.offer"
    _description = "beesdoo.shift.solidarity.offer"

    def _get_selection_status(self):
        return [
            ("draft", "Draft"),
            ("validated", "Validated"),
            ("cancelled", "Cancelled"),
        ]

    worker_id = fields.Many2one(
        "res.partner",
        domain=[
            ("is_worker", "=", True),
            ("working_mode", "in", ("regular", "irregular")),
            ("state", "not in", ("unsubscribed", "resigning")),
        ],
        string="worker",
    )

    state = fields.Selection(selection=_get_selection_status, default="draft")

    tmpl_dated_id = fields.Many2one(
        "beesdoo.shift.template.dated", string="Solidarity shift"
    )

    shift_id = fields.Many2one(
        "beesdoo.shift.shift", compute="_compute_shift_already_generated"
    )

    date = fields.Date(required=True, default=datetime.date(datetime.now()))

    @api.depends("tmpl_dated_id")
    def _compute_shift_already_generated(self):
        for record in self:
            # Get current date
            now = datetime.now()
            if not record.tmpl_dated_id:
                record.shift_id = False
            elif self.state == "validated":
                record.shift_id = False
            else:
                # Get the shift if it is already generated
                future_subscribed_shifts_rec = self.env["beesdoo.shift.shift"].search(
                    [
                        ("start_time", ">", now.strftime("%Y-%m-%d %H:%M:%S")),
                        ("start_time", "=", record.tmpl_dated_id.date),
                        ("task_template_id", "=", record.tmpl_dated_id.template_id.id),
                        ("worker_id", "=", None),
                    ],
                    limit=1,
                )
                # check if is there a shift generated
                if future_subscribed_shifts_rec:
                    record.shift_id = future_subscribed_shifts_rec
                    return True
                return False

    def counter(self):
        counter = 0
        for record in self:
            if record.state == "validated":
                counter += 1
        return counter

    def update_status(self):
        if self.tmpl_dated_id and self.worker_id:
            self.write({"state": "validated"})

    @api.multi
    def subscribe_shift(self):
        """
        Subscribe the user into the given shift
        this is done only if :
            *the user can subscribe
            *the given shift exist
            *the shift status is open (it isn't already subscribed)
            *the user hasn't done another exchange 2month before
        :return:
        """
        if self.state != "validated":
            # Get the wanted shift
            shift_rec = self.shift_id
            shift_rec.is_regular = True
            # Get the user
            shift_rec.write({"worker_id": self.worker_id.id})

            # update status
            self.update_status()
            if not self.shift_id.worker_id:
                return False
            return True
        return True
