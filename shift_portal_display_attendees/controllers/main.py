# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.http import request

from odoo.addons.shift_portal.controllers.main import WebsiteShiftController


class WebsiteShiftController(WebsiteShiftController):
    def available_shift_irregular_worker(
        self, irregular_enable_sign_up=False, nexturl=""
    ):
        res = super().available_shift_irregular_worker(
            irregular_enable_sign_up, nexturl
        )
        res["display_attendees"] = request.website.display_attendees_on_portal
        return res

    def get_compensation_shift_grid(self, shifts):
        res = super().get_compensation_shift_grid(shifts)
        res["display_attendees"] = request.website.display_attendees_on_portal
        return res

    def my_shift_next_shifts(self, partner=None):
        res = super().my_shift_next_shifts(partner)
        res["display_attendees"] = request.website.display_attendees_on_portal
        return res
