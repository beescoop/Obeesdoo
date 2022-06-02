from datetime import datetime
from itertools import groupby

from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.beesdoo_website_shift.controllers.main import WebsiteShiftController
from odoo.addons.beesdoo_website_shift.controllers.shift_grid_utils import (
    DisplayedShift,
    build_shift_grid,
)


class WebsiteShiftSwapController(WebsiteShiftController):
    def new_tmpl_dated(self, template_id, date):
        return (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .new(
                {
                    "template_id": template_id,
                    "date": date,
                }
            )
        )

    def exchanges_enabled(self):
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.enable_exchanges")
        )

    def solidarity_enabled(self):
        return (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.enable_solidarity")
        )

    def solidarity_counter_too_low(self):
        return request.env[
            "res.company"
        ]._company_default_get().solidarity_counter() <= int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.solidarity_counter_limit")
        )

    # Override /my/shift webpage controller
    @http.route("/my/shift", auth="user", website=True)
    def my_shift(self, **kw):
        res = super(WebsiteShiftSwapController, self).my_shift()
        template_context = res.qcontext
        template_context["request_solidarity"] = False

        if self.exchanges_enabled():
            template_context["exchanges_enabled"] = True
        else:
            template_context["exchanges_enabled"] = False

        if self.solidarity_enabled():
            template_context["solidarity_enabled"] = True
            if "request_solidarity" in kw:
                template_context["request_solidarity"] = kw["request_solidarity"]
        else:
            template_context["solidarity_enabled"] = False

        # Add feedback about the success of solidarity offer/request
        template_context["back_from_solidarity"] = False

        if "offer_success" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["offer_success"] = request.session.get("offer_success")
            del request.session["offer_success"]

        elif "offer_cancel" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["offer_cancel"] = request.session.get("offer_cancel")
            del request.session["offer_cancel"]

        elif "request_success" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["request_success"] = request.session.get("request_success")
            del request.session["request_success"]

        elif "request_success_irregular" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["request_success_irregular"] = request.session.get(
                "request_success_irregular"
            )
            del request.session["request_success_irregular"]

        elif "request_cancel" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["request_cancel"] = request.session.get("request_cancel")
            del request.session["request_cancel"]

        elif "request_cancel_irregular" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["request_cancel_irregular"] = request.session.get(
                "request_cancel_irregular"
            )
            del request.session["request_cancel_irregular"]

        elif "shift_number_limit" in request.session:
            template_context["back_from_solidarity"] = True
            template_context["fail"] = True
            template_context["shift_number_limit"] = request.session.get(
                "shift_number_limit"
            )
            del request.session["shift_number_limit"]

        return request.render(res.template, template_context)

    @http.route("/my/shift/swaping/<int:template_id>/<string:date>", website=True)
    def swaping_shift(self, template_id, date, **kw):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        # Save the swaping tmpl_dated in the user session
        request.session["template_id"] = template_id
        request.session["date"] = date

        shift_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = shift_date - datetime.now()
        if "from_mail" in kw:
            request.session["from_mail"] = kw["from_mail"]
            return request.redirect("/my/shift/possible/match")
        elif (
            delta.days
            > int(
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("beesdoo_shift.day_limit_swap")
            )
            or "planned" in kw
        ):
            return request.redirect("/my/shift/possible/match")
        else:
            return request.redirect("/my/shift/swap")

    @http.route("/my/shift/swap", website=True)
    def get_next_shifts_to_swap(self, **kw):
        """
        Personnal page to choose a shift to swap
        """
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        # Get template and date from session
        template_id = request.session["template_id"]
        date = request.session["date"]
        # Create new tmpl_dated
        my_tmpl_dated = self.new_tmpl_dated(template_id, date)

        # Get next shifts
        display_all = False
        if "display_all" in kw and kw["display_all"]:
            # Get all next shifts
            next_shifts = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .get_available_tmpl_dated(sort_date_desc=True)
            )
            display_all = True
        else:
            # Get only underpopulated shifts
            next_shifts = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .get_underpopulated_tmpl_dated(sort_date_desc=True)
            )

        user = request.env["res.users"].sudo().browse(request.uid)

        # Remove the already subscribed shifts
        possible_shifts = next_shifts.remove_already_subscribed_shifts(user.partner_id)

        # Create template context
        template_context = {}
        template_context.update(self.get_shift_grid(possible_shifts))
        template_context["exchanged_tmpl_dated"] = my_tmpl_dated
        template_context["all_shifts"] = display_all

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_tmpl_dated",
            template_context,
        )

    @http.route(
        "/my/shift/swap/subscribe/<int:template_wanted>/<string:date_wanted>",
        website=True,
    )
    def swap_shift(self, template_wanted, date_wanted):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_id,
                    "date": date,
                }
            )
        )

        tmpl_dated_wanted = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_wanted,
                    "date": date_wanted,
                }
            )
        )
        # Check if the shift limit is not reached
        try:
            user.partner_id.sudo().check_shift_number_limit(tmpl_dated_wanted)
        except UserError:
            request.session["shift_number_limit"] = True
            return request.redirect("/my/shift")

        request.env["beesdoo.shift.swap"].sudo().create(
            {
                "worker_id": user.partner_id.id,
                "exchanged_tmpl_dated_id": my_tmpl_dated.id,
                "wanted_tmpl_dated_id": tmpl_dated_wanted.id,
            }
        )

        return request.redirect("/my/shift")

    @http.route("/my/shift/swap/no_result", website=True)
    def no_result_shift_swap(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        date = request.session["date"]
        shift_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = shift_date - datetime.now()
        if delta.days > int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.day_limit_request_exchange")
        ):
            return request.redirect("/my/shift/possible/match")
        else:
            return request.redirect("/my/shift/swap?display_all=1")

    @http.route("/my/shift/possible/match", website=True)
    def get_possible_match(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        template_id = request.session["template_id"]
        date = request.session["date"]
        exchanged_tmpl_dated = self.new_tmpl_dated(template_id, date)
        possible_matches = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .get_possible_match(exchanged_tmpl_dated)
        )

        template_context = {
            "possible_matches": possible_matches,
            "exchanged_tmpl_dated": exchanged_tmpl_dated,
            "from_mail": False,
        }
        if "from_mail" in request.session:
            template_context["from_mail"] = request.session["from_mail"]
            del request.session["from_mail"]

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_possible_match",
            template_context,
        )

    @http.route("/my/shift/possible/match/no_result", website=True)
    def no_result_possible_match(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        date = request.session["date"]
        shift_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        delta = shift_date - datetime.now()
        if delta.days > int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.day_limit_exchange_with_same_timeslot")
        ):
            return request.redirect("/my/shift/possible/shift")
        else:
            return request.redirect("/my/shift/select/same_timeslot")

    @http.route("/my/shift/possible/shift", website=True)
    def get_possible_shift(self, **post):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        template_id = request.session["template_id"]
        date = request.session["date"]
        user = request.env["res.users"].sudo().browse(request.uid)

        if request.httprequest.method == "POST":
            tmpl_dated_index = request.httprequest.form.getlist("selected_tmpl_dated")
            wanted_index_list = []
            for index in tmpl_dated_index:
                wanted_index_list.append(int(index))
            exchanged_tmpl_dated = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .create(
                    {
                        "template_id": template_id,
                        "date": date,
                    }
                )
            )
            asked_tmpl_dated = request.env["beesdoo.shift.template.dated"].sudo()
            for index, template in enumerate(
                request.session["possible_tmpl_dated_list"]
            ):
                if index in wanted_index_list:
                    asked_tmpl_dated |= asked_tmpl_dated.sudo().create(
                        {
                            "date": template["date"],
                            "template_id": template["template_id"],
                        }
                    )

            # Check that the shift number limit is not reached
            impossible_tmpl_dated = []
            for template in asked_tmpl_dated:
                try:
                    user.partner_id.sudo().check_shift_number_limit(template)
                except UserError:
                    impossible_tmpl_dated.append(template)
            if impossible_tmpl_dated:
                return request.render(
                    "beesdoo_website_shift_swap"
                    ".website_shift_swap_impossible_exchange_request",
                    {
                        "tmpl_dated": impossible_tmpl_dated,
                    },
                )

            request.env["beesdoo.shift.exchange_request"].sudo().create(
                {
                    "worker_id": user.partner_id.id,
                    "exchanged_tmpl_dated_id": exchanged_tmpl_dated.id,
                    "asked_tmpl_dated_ids": [(6, False, asked_tmpl_dated.ids)],
                }
            )
            return request.redirect("/my/shift")

        exchanged_tmpl_dated = self.new_tmpl_dated(template_id, date)

        period = int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.day_limit_ask_for_exchange")
        )
        next_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .get_available_tmpl_dated(nb_days=period)
        )

        # Remove the already subscribed shifts
        possible_tmpl_dated = next_tmpl_dated.remove_already_subscribed_shifts(
            user.partner_id
        )

        possible_tmpl_dated_list = []
        for template in possible_tmpl_dated:
            possible_tmpl_dated_list.append(
                {
                    "template_id": template.template_id.id,
                    "date": template.date,
                }
            )
        request.session["possible_tmpl_dated_list"] = possible_tmpl_dated_list

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_possible_tmpl_dated",
            {
                "possible_tmpl_dated": possible_tmpl_dated,
                "exchanged_tmpl_dated": exchanged_tmpl_dated,
            },
        )

    @http.route("/my/shift/select/same_timeslot", website=True)
    def select_same_timeslot_other_weeks(self, **post):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        template_id = request.session["template_id"]
        date = request.session["date"]

        if request.httprequest.method == "POST":
            tmpl_dated_index = request.httprequest.form.getlist("selected_tmpl_dated")
            wanted_index_list = []
            for index in tmpl_dated_index:
                wanted_index_list.append(int(index))
            exchanged_tmpl_dated = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .create(
                    {
                        "template_id": template_id,
                        "date": date,
                    }
                )
            )
            asked_tmpl_dated = request.env["beesdoo.shift.template.dated"].sudo()
            for index, template in enumerate(
                request.session["possible_tmpl_dated_list"]
            ):
                if index in wanted_index_list:
                    asked_tmpl_dated |= asked_tmpl_dated.sudo().create(
                        {
                            "date": template["date"],
                            "template_id": template["template_id"],
                        }
                    )
            user = request.env["res.users"].sudo().browse(request.uid)
            exchange_request = (
                request.env["beesdoo.shift.exchange_request"]
                .sudo()
                .create(
                    {
                        "worker_id": user.partner_id.id,
                        "exchanged_tmpl_dated_id": exchanged_tmpl_dated.id,
                        "asked_tmpl_dated_ids": [(6, False, asked_tmpl_dated.ids)],
                    }
                )
            )

            # Contact the workers of the wanted timeslots
            exchange_request.send_mail_wanted_tmpl_dated()

            return request.redirect("/my/shift")

        exchanged_tmpl_dated = self.new_tmpl_dated(template_id, date)

        period = int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.day_limit_ask_for_exchange")
        )
        possible_tmpl_dated = exchanged_tmpl_dated.get_tmpl_dated_same_timeslot(period)

        possible_tmpl_dated_list = []
        for template in possible_tmpl_dated:
            possible_tmpl_dated_list.append(
                {
                    "template_id": template.template_id.id,
                    "date": template.date,
                }
            )
        request.session["possible_tmpl_dated_list"] = possible_tmpl_dated_list

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_possible_tmpl_dated",
            {
                "possible_tmpl_dated": possible_tmpl_dated,
                "exchanged_tmpl_dated": exchanged_tmpl_dated,
            },
        )

    @http.route("/my/request", website=True)
    def my_request(self):
        # Get current user
        cur_user = request.env["res.users"].sudo().browse(request.uid)

        # Get exchange requests
        exchange_request_list = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("worker_id", "=", cur_user.partner_id.id)])
        )
        exchange_requests = []
        for rec in exchange_request_list:
            exchange_requests.append(
                {
                    "my_request": rec,
                    "matching_request": request.env["beesdoo.shift.exchange_request"]
                    .sudo()
                    .matching_request(
                        rec.asked_tmpl_dated_ids, rec.exchanged_tmpl_dated_id
                    ),
                }
            )

        # Get solidarity requests
        solidarity_requests = (
            request.env["beesdoo.shift.solidarity.request"]
            .sudo()
            .search([("worker_id", "=", cur_user.partner_id.id)])
        )

        return request.render(
            "beesdoo_website_shift_swap.my_request",
            {
                "exchange_requests": exchange_requests,
                "solidarity_requests": solidarity_requests,
                "regular": True
                if cur_user.partner_id.working_mode == "regular"
                else False,
                "now": datetime.now(),
                "exchanges_enabled": True if self.exchanges_enabled() else False,
                "solidarity_enabled": True if self.solidarity_enabled() else False,
            },
        )

    @http.route(
        "/my/shift/validate/matching_request/<int:matching_request_id>", website=True
    )
    def validate_matching_request(self, matching_request_id):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        cur_user = request.env["res.users"].sudo().browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_id,
                    "date": date,
                }
            )
        )
        matching_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .browse(matching_request_id)
        )
        # Check if the shift limit is not reached
        try:
            cur_user.partner_id.sudo().check_shift_number_limit(
                matching_request.exchanged_tmpl_dated_id
            )
        except UserError:
            request.session["shift_number_limit"] = True
            return request.redirect("/my/shift")

        data = {
            "worker_id": cur_user.partner_id.id,
            "exchanged_tmpl_dated_id": my_tmpl_dated.id,
            "asked_tmpl_dated_ids": [
                (6, False, matching_request.exchanged_tmpl_dated_id.ids)
            ],
            "validate_request_id": matching_request_id,
        }
        new_request = request.env["beesdoo.shift.exchange_request"].sudo().create(data)
        matching_request.sudo().send_mail_matching_request(new_request)
        return request.redirect("/my/request")

    @http.route(
        "/my/shift/validate/matching/validate/request/"
        "<int:my_request_id>/<int:match_request_id>",
        website=True,
    )
    def validate_matching_validate_request(self, my_request_id, match_request_id):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)
        match_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .browse(match_request_id)
        )
        # Check if the shift limit is not reached
        try:
            user.partner_id.sudo().check_shift_number_limit(
                match_request.exchanged_tmpl_dated_id
            )
        except UserError:
            request.session["shift_number_limit"] = True
            return request.redirect("/my/shift")

        exchange_data = {
            "first_request_id": my_request_id,
            "second_request_id": match_request_id,
        }
        request.env["beesdoo.shift.exchange"].sudo().create(exchange_data)
        return request.redirect("/my/shift")

    # Solidarity shift offer
    @http.route("/my/shift/solidarity/offer", website=True)
    def get_next_shift_for_solidarity(self, **kw):
        """
        Page to choose a shift to subscribe for solidarity
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        # Check if user can offer solidarity shifts
        if user.cooperative_status_ids.sr < 0 or user.cooperative_status_ids.sc < 0:
            return request.render(
                "beesdoo_website_shift_swap."
                "website_shift_swap_offer_solidarity_impossible"
            )

        # Get the next shifts
        display_all = False
        if "display_all" in kw and kw["display_all"]:
            # Get all next shifts
            next_shifts = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .get_available_tmpl_dated(sort_date_desc=True)
            )
            display_all = True
        else:
            # Get only underpopulated shifts
            next_shifts = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .get_underpopulated_tmpl_dated(sort_date_desc=True)
            )

        # Remove the already subscribed shifts
        next_possible_shifts = next_shifts.remove_already_subscribed_shifts(
            user.partner_id
        )

        # Create template context
        template_context = {}
        template_context.update(self.get_shift_grid(next_possible_shifts))
        template_context["all_shifts"] = display_all

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_select_solidarity",
            template_context,
        )

    @http.route(
        "/my/shift/solidarity/offer/select/<int:template_wanted>/<string:date_wanted>",
        website=True,
    )
    def subscribe_to_shift_for_solidarity(self, template_wanted, date_wanted):
        """
        Create the solidarity offer based on the selected shift data
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        tmpl_dated_wanted = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_wanted,
                    "date": date_wanted,
                }
            )
        )
        try:
            user.partner_id.sudo().check_shift_number_limit(tmpl_dated_wanted)
        except UserError:
            request.session["shift_number_limit"] = True
            return request.redirect("/my/shift")
        data = {
            "worker_id": user.partner_id.id,
            "tmpl_dated_id": tmpl_dated_wanted.id,
        }
        request.env["beesdoo.shift.solidarity.offer"].sudo().create(data)
        request.session["offer_success"] = True
        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/solidarity/offer/cancel/<int:solidarity_offer_id>",
        website=True,
    )
    def cancel_solidarity_offer(self, solidarity_offer_id):
        """
        Cancel a solidarity offer
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        solidarity_offer = (
            request.env["beesdoo.shift.solidarity.offer"]
            .sudo()
            .browse(solidarity_offer_id)
        )

        # Check if the offer is not too close in time
        if solidarity_offer.check_offer_date_too_close():
            return request.render(
                "beesdoo_website_shift_swap."
                "website_shift_swap_cancel_solidarity_offer_impossible"
            )

        solidarity_offer.cancel_solidarity_offer()
        request.session["offer_cancel"] = True
        return request.redirect("/my/shift")

    # Solidarity shift request
    @http.route(
        "/my/shift/solidarity/request/<int:template_id>/<string:date>", website=True
    )
    def prepare_request_solidarity_shift(self, template_id, date):
        """
        Store the dated template and the date of the shift to request solidarity
        (regular workers only)
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")
        if self.solidarity_counter_too_low():
            raise Forbidden(
                "Solidarity counter is too low, requesting solidarity is impossible"
            )

        request.session["template_id"] = template_id
        request.session["date"] = date
        return request.redirect("/my/shift/solidarity/request")

    @http.route("/my/shift/solidarity/request", website=True)
    def request_solidarity_shift(self, **post):
        """
        Page to give the reason for a solidarity request
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")
        if self.solidarity_counter_too_low():
            raise Forbidden(
                "Solidarity counter is too low, requesting solidarity is impossible"
            )

        user = request.env["res.users"].sudo().browse(request.uid)
        regular = False
        if user.partner_id.working_mode == "regular":
            regular = True
            template_id = request.session["template_id"]
            date = request.session["date"]

        if request.httprequest.method == "POST":
            if regular:
                non_realisable_tmpl_dated = (
                    request.env["beesdoo.shift.template.dated"]
                    .sudo()
                    .create(
                        {
                            "template_id": template_id,
                            "date": date,
                        }
                    )
                )
            reason = request.httprequest.form.get("reason")
            data = {
                "worker_id": user.partner_id.id,
                "tmpl_dated_id": non_realisable_tmpl_dated.id if regular else False,
                "reason": reason,
            }
            request.env["beesdoo.shift.solidarity.request"].sudo().create(data)
            if regular:
                request.session["request_success"] = True
            else:
                request.session["request_success_irregular"] = True
            return request.redirect("/my/shift")

        if regular:
            tmpl_dated = self.new_tmpl_dated(template_id, date)
            can_request = request.env[
                "beesdoo.shift.solidarity.request"
            ].check_solidarity_requests_number(
                user.partner_id, datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            )
        else:
            tmpl_dated = False
            can_request = request.env[
                "beesdoo.shift.solidarity.request"
            ].check_solidarity_requests_number(user.partner_id)

        if can_request:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_request_solidarity",
                {
                    "tmpl_dated": tmpl_dated,
                },
            )
        else:
            # User has reached maximum amount of solidarity requests
            return request.render(
                "beesdoo_website_shift_swap"
                ".website_shift_swap_request_solidarity_impossible"
            )

    @http.route(
        "/my/shift/solidarity/request/cancel/<int:solidarity_request_id>",
        website=True,
    )
    def cancel_solidarity_request(self, solidarity_request_id):
        """
        Cancel a solidarity request
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        solidarity_request = (
            request.env["beesdoo.shift.solidarity.request"]
            .sudo()
            .browse(solidarity_request_id)
        )

        solidarity_request.cancel_solidarity_request()
        if solidarity_request.worker_id.working_mode == "regular":
            request.session["request_cancel"] = True
        else:
            request.session["request_cancel_irregular"] = True
        return request.redirect("/my/shift")

    def my_shift_next_shifts(self):
        """
        Override my_shift_next_shifts method to sort shifts by date
        after taking into account exchanges and solidarity
        """
        res = super(WebsiteShiftSwapController, self).my_shift_next_shifts()
        res["subscribed_shifts"] = sorted(
            res["subscribed_shifts"], key=lambda r: r.start_time
        )
        return res

    def get_shift_grid(self, shifts):
        """
        Return template variables for
        'beesdoo_website_shift_swap.available_underpopulated_shifts_grid'
        """
        groupby_iter = groupby(
            shifts,
            lambda s: (s.template_id, s.date, s.template_id.task_type_id),
        )

        displayed_shifts = []
        for keys, grouped_shifts in groupby_iter:
            task_template, start_time, task_type = keys
            shift_list = list(grouped_shifts)
            displayed_shifts.append(
                DisplayedShift(
                    shift_list[0],
                    None,
                    None,
                    None,
                )
            )

        shift_weeks = build_shift_grid(displayed_shifts)
        return {
            "shift_weeks": shift_weeks,
        }
