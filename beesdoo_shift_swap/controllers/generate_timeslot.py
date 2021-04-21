from datetime import datetime, timedelta

from pytz import timezone, utc

from odoo import http
from odoo.fields import Datetime
from odoo.http import request

#from odoo.addons.beesdoo_shift.models.planning import float_to_time

class BeesdooRegularSwitchShift(http.Controller):

    @http.route("/my/timeslot", type="http",auth="none")
    def my_timeslot(self, **kw):
        my_timeslot = request.env["beesdoo.shift.timeslots_date"].sudo().search([
            ("date", ">", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ],
            limit=1
        )

        timeslot = request.env["beesdoo.shift.subscribed_underpopulated_shift"].sudo().display_underpopulated_shift(my_timeslot)
        #timeslot = request.env["beesdoo.shift.timeslots_date"].sudo().display_timeslot(my_timeslot)
        return str(timeslot)





