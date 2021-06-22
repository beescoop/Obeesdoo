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

    def shift_to_timeslot(self,my_shift):
        list_shift = []
        list_shift.append(my_shift)
        my_timeslot = request.env["beesdoo.shift.template.dated"].sudo().swap_shift_to_timeslot(list_shift)
        return my_timeslot



    @http.route("/my/shift/swaping/<int:shift>")
    def swaping_shift(self,shift):
        user = request.env["res.users"].browse(request.uid)
        now = datetime.now()
        shift_date = shift.start_time
        delta = shift_date - now
        if delta.days <= 56 :
            if delta.days <= 28 :
                return self.get_underpopulated_shift(shift)

    @http.route("/my/shift/<int:my_shift>/underpopulated/swap")
    def get_underpopulated_shift(self,my_shift):
        """
        Personal page for swaping your shifts
        :return:
        """
        my_timeslot = self.shift_to_timeslot(my_shift)
        my_available_shift = (
            request.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .display_underpopulated_shift(my_timeslot)
        )
        return request.render("beesdoo_website_shift_swap.website_shift_swap_swap",
            {
                "underpopulated_shift" : my_available_shift
            }
        )

    @http.route("/my/shift/<int:my_shift>/possible/shift")
    def get_possible_shift(self,my_shift):

        my_timeslot = self.shift_to_timeslot(my_shift)
        possible_timeslot = request.env["beesdoo.shift.template.dated"].sudo().display_timeslot(my_timeslot)
        return request.render ("beesdoo_website_shift_swap.website_shift_swap_possible_timeslot",
                {
                    "possible_timeslot": possible_timeslot
               })

    @http.route("/my/shift/matching/request")
    def my_match(self):
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        my_exchanges = request.env["beesdoo.shift.exchange_request"].sudo().search([
            ('worker_id','=',cur_user.id)
        ])
        matchs = request.env["beesdoo.shift.exchange_request"]
        for exchange in my_exchanges :
            matchs |= request.env["beesdoo.shift.exchange_request"].matching_request(exchange.asked_timeslot_ids,exchange.exchanged_timeslot_id)

        return request.render("beesdoo_website_shift_swap.website_shift_swap_matching_request",
                              {
                                  "matching_request":matchs
                              })