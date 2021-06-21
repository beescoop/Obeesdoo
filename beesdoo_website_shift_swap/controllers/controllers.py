# -*- coding: utf-8 -*-
from odoo import http

from datetime import datetime, timedelta
from itertools import groupby

from pytz import timezone, utc

from odoo import http
from odoo.fields import Datetime
from odoo.http import request

#from Obeesdoo.beesdoo_shift.models.planning import float_to_time
#from Obeesdoo.beesdoo_website_shift.controllers import main

class WebsiteShiftSwapController(http.Controller):

    @http.route("/my/shift/<string:my_shift>/choose/swap")
    def my_available_shift(self,my_shift):
        """
        Personal page for swaping your shifts
        :return:
        """
        my_available_shift = (
            request.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .get_underpopulated_shift(my_shift)
        )
        return request.render ("beesdoo_website_shift_swap.website_shift_swap_swap",
            {
            "available_shift" : my_available_shift
            }
        )
