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

    @http.route("/my/shift/choose/swap")
    def display_shift(self):
     return('<h1>yolo</h1>')
