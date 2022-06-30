from datetime import datetime
from itertools import groupby

from werkzeug.exceptions import Forbidden

from odoo import _, http
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

    def exchange_request_exists(self, worker_id: int, template_id: int, date: str):
        """ Return True if an exchange request exists for the given parameters """
        return any(
            r.exchanged_tmpl_dated_id.template_id.id == template_id
            and str(r.exchanged_tmpl_dated_id.date) == date
            for r in request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search(
                [
                    ("worker_id", "=", worker_id),
                    ("status", "not in", ["done", "cancelled"]),
                ],
            )
        )

    def max_shifts_number_message(self):
        return _("You have reached the maximum number of shifts per day or month.")

    def no_shift_match_info_message(self):
        return _("The information you provided does not match any existing shift.")

    def exchange_already_exists_message(self):
        return _("You have already requested an exchange for this shift.")

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

        # Clear session
        if "template_id" in request.session:
            del request.session["template_id"]
        if "date" in request.session:
            del request.session["date"]
        if "exchanged_tmpl_dated" in request.session:
            del request.session["exchanged_tmpl_dated"]
        if "partner_id" in request.session:
            del request.session["partner_id"]
        if "from_mail" in request.session:
            del request.session["from_mail"]

        return request.render(res.template, template_context)

    @http.route(
        "/my/shift/exchange/<int:template_id>/<string:date>/contact",
        auth="user",
        website=True,
    )
    def contact_coop_planned_exchange(self, template_id, date, **post):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        if request.httprequest.method == "POST":
            email = request.httprequest.form.get("coop_mail")
            asked_shift_date = request.httprequest.form.get("shift_date")

            asked_worker = (
                request.env["res.partner"]
                .sudo()
                .search([("email", "=", email)], limit=1)
            )

            if not asked_worker:
                request.session["error_message"] = self.no_shift_match_info_message()
                return request.redirect("/my/shift")
            elif asked_worker.working_mode != "regular":
                request.session["error_message"] = _(
                    "This worker is not regular, shift exchanges "
                    "are only available between regular workers."
                )
                return request.redirect("/my/shift")

            next_shifts_other_coop = self.my_shift_next_shifts(asked_worker)

            if not any(
                shift.start_time.strftime("%Y-%m-%d") == asked_shift_date
                for shift in next_shifts_other_coop["subscribed_shifts"]
            ):
                request.session["error_message"] = self.no_shift_match_info_message()
                return request.redirect("/my/shift")

            exchanged_shift_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            asked_shift_date = datetime.strptime(asked_shift_date, "%Y-%m-%d")

            # Send a mail to the asked_worker
            template = request.env.ref(
                "beesdoo_shift_swap.planned_exchange_contact_coop", False
            ).sudo()
            email_values = {
                "partner_to": asked_worker,
                "template_id": request.env["beesdoo.shift.template"]
                .sudo()
                .browse(template_id),
                "exchanged_shift_date": exchanged_shift_date,
                "asked_shift_date": asked_shift_date,
            }
            template.with_context(email_values).send_mail(user.partner_id.id)

            request.session["success_message"] = _(
                "The cooperator has been contacted. "
                "You will be notified if he/she accepts your exchange."
            )
            return request.redirect("/my/shift")

        # Check that an exchange request doesn't already exist for this shift
        if self.exchange_request_exists(user.partner_id.id, template_id, date):
            request.session["error_message"] = self.exchange_already_exists_message()
            return request.redirect("/my/shift")

        # Create new tmpl_dated
        exchanged_tmpl_dated = self.new_tmpl_dated(template_id, date)

        return request.render(
            "beesdoo_website_shift_swap.contact_coop_for_planned_exchange",
            {
                "exchanged_tmpl_dated": exchanged_tmpl_dated,
            },
        )

    @http.route(
        "/my/shift/exchange/<int:partner_id>/<int:template_id>/<string:exchanged_date>"
        "/validate/<string:personal_date>",
        auth="user",
        website=True,
    )
    def validate_planned_exchange(
        self, partner_id, template_id, exchanged_date, personal_date
    ):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        request.session["partner_id"] = partner_id
        request.session["template_id"] = template_id
        request.session["date"] = exchanged_date

        # Create new tmpl_dated
        exchanged_tmpl_dated = self.new_tmpl_dated(template_id, exchanged_date)

        # Get the shifts to exchange
        subscribed_shifts = self.my_shift_next_shifts()["subscribed_shifts"]
        possible_shifts = []
        for shift in subscribed_shifts:
            if shift.start_time.strftime("%Y-%m-%d") == personal_date:
                possible_shifts.append(shift)

        # Create template context
        template_context = {
            "partner_id": request.env["res.partner"].sudo().browse(partner_id),
            "exchanged_tmpl_dated": exchanged_tmpl_dated,
            "subscribed_shifts": possible_shifts,
        }

        return request.render(
            "beesdoo_website_shift_swap.validate_planned_exchange",
            template_context,
        )

    @http.route(
        "/my/shift/exchange/validate/select/<int:template_id>/<string:date>",
        auth="user",
        website=True,
    )
    def validate_planned_exchange_select(self, template_id, date):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if (
            "partner_id" not in request.session
            or "template_id" not in request.session
            or "date" not in request.session
        ):
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

        user = request.env["res.users"].sudo().browse(request.uid)

        # Check that an exchange request doesn't already exist for this shift
        if self.exchange_request_exists(user.partner_id.id, template_id, date):
            request.session["error_message"] = self.exchange_already_exists_message()
            return request.redirect("/my/shift")

        wanted_template_id = request.session["template_id"]
        wanted_date = request.session["date"]
        wanted_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": wanted_template_id,
                    "date": wanted_date,
                }
            )
        )

        # Check shift number limit
        try:
            user.partner_id.sudo().check_shift_number_limit(wanted_tmpl_dated)
        except UserError:
            request.session["error_message"] = self.max_shifts_number_message()
            return request.redirect("/my/shift")

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

        first_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .create(
                {
                    "worker_id": request.session["partner_id"],
                    "exchanged_tmpl_dated_id": wanted_tmpl_dated.id,
                    "asked_tmpl_dated_ids": [(6, False, exchanged_tmpl_dated.ids)],
                }
            )
        )

        new_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .create(
                {
                    "worker_id": user.partner_id.id,
                    "exchanged_tmpl_dated_id": exchanged_tmpl_dated.id,
                    "asked_tmpl_dated_ids": [(6, False, wanted_tmpl_dated.ids)],
                    "validate_request_id": first_request.id,
                }
            )
        )

        first_request.sudo().send_mail_matching_request(new_request)

        # Clear session
        del request.session["partner_id"]
        del request.session["template_id"]
        del request.session["date"]

        return request.redirect("/my/request")

    @http.route(
        "/my/shift/swaping/<int:template_id>/<string:date>", auth="user", website=True
    )
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

    @http.route("/my/shift/swap", auth="user", website=True)
    def get_next_shifts_to_swap(self, **kw):
        """
        Personnal page to choose a shift to swap
        """
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

        # Get template and date from session
        template_id = request.session["template_id"]
        date = request.session["date"]

        # Create new tmpl_dated
        my_tmpl_dated = self.new_tmpl_dated(template_id, date)

        # Get next shifts
        display_all = False
        if "display_all" in request.session and request.session["display_all"]:
            # Get all next shifts
            next_shifts = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .get_available_tmpl_dated(sort_date_desc=True)
            )
            display_all = True
            del request.session["display_all"]
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
        auth="user",
        website=True,
    )
    def swap_shift(self, template_wanted, date_wanted):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

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

        # Clear session
        del request.session["template_id"]
        del request.session["date"]

        # Check if the shift limit is not reached
        try:
            user.partner_id.sudo().check_shift_number_limit(tmpl_dated_wanted)
        except UserError:
            request.session["error_message"] = self.max_shifts_number_message()
            return request.redirect("/my/shift")

        request.env["beesdoo.shift.swap"].sudo().create(
            {
                "worker_id": user.partner_id.id,
                "exchanged_tmpl_dated_id": my_tmpl_dated.id,
                "wanted_tmpl_dated_id": tmpl_dated_wanted.id,
            }
        )

        return request.redirect("/my/shift")

    @http.route("/my/shift/swap/no_result", auth="user", website=True)
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
            request.session["display_all"] = True
            return request.redirect("/my/shift/swap")

    @http.route("/my/shift/swap/not_found", auth="user", website=True)
    def not_found_shift_swap(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

        user = request.env["res.users"].sudo().browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]

        shift = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("worker_id", "=", user.partner_id.id),
                    ("task_template_id", "=", template_id),
                    ("start_time", "=", date),
                ],
                limit=1,
            )
        )

        if shift:
            shift.write(
                {"worker_id": False, "is_regular": False, "is_compensation": False}
            )
            user.partner_id.cooperative_status_ids.sc -= 1
            template = self.env["beesdoo.shift.template"].browse(template_id)
            self.env["beesdoo.shift.exchange_request"].cancel_matching_requests(
                user.partner_id, template, date
            )
            request.session["success_message"] = _(
                "You have been unsubscribed to this shift."
            )
        else:
            request.session["error_message"] = _(
                "This shift is not generated. Unsubscription impossible."
            )

        # Clear session
        del request.session["template_id"]
        del request.session["date"]

        return request.redirect("/my/shift")

    @http.route("/my/shift/possible/match", auth="user", website=True)
    def get_possible_match(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

        user = request.env["res.users"].sudo().browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]

        # Check that an exchange request doesn't already exist for this shift
        if self.exchange_request_exists(user.partner_id.id, template_id, date):
            request.session["error_message"] = self.exchange_already_exists_message()
            return request.redirect("/my/shift")

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

    @http.route("/my/shift/possible/match/no_result", auth="user", website=True)
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

    @http.route("/my/shift/possible/shift", auth="user", website=True)
    def get_possible_shift(self, **post):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

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

            # Clear session
            del request.session["template_id"]
            del request.session["date"]
            del request.session["possible_tmpl_dated_list"]

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

    @http.route("/my/shift/select/same_timeslot", auth="user", website=True)
    def select_same_timeslot_other_weeks(self, **post):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

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

            # Clear session
            del request.session["template_id"]
            del request.session["date"]

            return request.redirect("/my/request")

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

    @http.route("/my/request", auth="user", website=True)
    def my_request(self):
        # Get current user
        cur_user = request.env["res.users"].sudo().browse(request.uid)

        request_number_limit = int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_website_shift_swap.request_number_limit")
        )

        # Get exchange requests
        exchange_request_list = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search(
                [("worker_id", "=", cur_user.partner_id.id)],
                order="create_date desc",
                limit=request_number_limit,
            )
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
            .search(
                [("worker_id", "=", cur_user.partner_id.id)],
                order="create_date desc",
                limit=request_number_limit,
            )
        )

        return request.render(
            "beesdoo_website_shift_swap.my_request",
            {
                "exchange_requests": exchange_requests,
                "solidarity_requests": solidarity_requests,
                "regular": cur_user.partner_id.working_mode == "regular",
                "now": datetime.now(),
                "exchanges_enabled": self.exchanges_enabled(),
                "solidarity_enabled": self.solidarity_enabled(),
            },
        )

    @http.route("/my/request/cancel/<int:request_id>", auth="user", website=True)
    def cancel_exchange_request(self, request_id):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        # Get exchange request
        exchange_request = (
            request.env["beesdoo.shift.exchange_request"].sudo().browse(request_id)
        )

        # Check if the user is the owner of the request
        if exchange_request.worker_id.id != user.partner_id.id:
            raise Forbidden("You are not allowed to cancel this request")

        if exchange_request.cancel_exchange_request():
            request.session["success_message"] = _("Your request has been cancelled.")
        else:
            request.session["error_message"] = _(
                "Your request could not be cancelled, "
                "Please note that validated exchanges cannot be cancelled."
            )

        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/validate/matching_request/<int:matching_request_id>",
        auth="user",
        website=True,
    )
    def validate_matching_request(self, matching_request_id):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")
        if "template_id" not in request.session or "date" not in request.session:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
            )

        cur_user = request.env["res.users"].sudo().browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]
        # Clear session
        del request.session["template_id"]
        del request.session["date"]

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
            request.session["error_message"] = self.max_shifts_number_message()
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
        auth="user",
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

        # Check if the user is the owner of the request
        my_request = (
            request.env["beesdoo.shift.exchange_request"].sudo().browse(my_request_id)
        )
        if my_request.worker_id.id != user.partner_id.id:
            raise Forbidden("You are not allowed to validate this request")

        # Check if the shift limit is not reached
        try:
            user.partner_id.sudo().check_shift_number_limit(
                match_request.exchanged_tmpl_dated_id
            )
        except UserError:
            request.session["error_message"] = self.max_shifts_number_message()
            return request.redirect("/my/shift")

        exchange_data = {
            "first_request_id": my_request_id,
            "second_request_id": match_request_id,
        }
        request.env["beesdoo.shift.exchange"].sudo().create(exchange_data)
        return request.redirect("/my/shift")

    # Solidarity shift offer
    @http.route("/my/shift/solidarity/offer", auth="user", website=True)
    def get_next_shift_for_solidarity(self, **kw):
        """
        Page to choose a shift to subscribe for solidarity
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        # Check if user can offer solidarity shifts
        status = user.cooperative_status_ids
        if (status.sr + status.sc) < 0:
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
        auth="user",
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
            request.session["error_message"] = self.max_shifts_number_message()
            return request.redirect("/my/shift")
        data = {
            "worker_id": user.partner_id.id,
            "tmpl_dated_id": tmpl_dated_wanted.id,
        }
        request.env["beesdoo.shift.solidarity.offer"].sudo().create(data)
        request.session["success_message"] = _(
            "You have been subscribed to a solidarity shift."
        )
        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/solidarity/offer/cancel/<int:solidarity_offer_id>",
        auth="user",
        website=True,
    )
    def cancel_solidarity_offer(self, solidarity_offer_id):
        """
        Cancel a solidarity offer
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        user = request.env["res.users"].sudo().browse(request.uid)

        solidarity_offer = (
            request.env["beesdoo.shift.solidarity.offer"]
            .sudo()
            .browse(solidarity_offer_id)
        )

        # Check if the user is the owner of the offer
        if solidarity_offer.worker_id.id != user.partner_id.id:
            raise Forbidden("You are not allowed to cancel this offer")

        # Check if the offer is not too close in time
        if solidarity_offer.check_offer_date_too_close():
            return request.render(
                "beesdoo_website_shift_swap."
                "website_shift_swap_cancel_solidarity_offer_impossible"
            )

        solidarity_offer.cancel_solidarity_offer()
        request.session["success_message"] = _(
            "Your solidarity shift has been cancelled."
        )
        return request.redirect("/my/shift")

    # Solidarity shift request
    @http.route("/my/shift/solidarity/request/past", auth="user", website=True)
    def get_past_shift_to_request_solidarity(self):
        """
        Calculate the last not attended shift for a regular worker
        """
        if not self.solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")
        if self.solidarity_counter_too_low():
            raise Forbidden(
                "Solidarity counter is too low, requesting solidarity is impossible"
            )

        user = request.env["res.users"].sudo().browse(request.uid)

        absent_states = request.env["beesdoo.shift.shift"].sudo().get_absent_state()
        not_attended_shift = (
            request.env["beesdoo.shift.shift"]
            .sudo()
            .search(
                [
                    ("worker_id", "=", user.partner_id.id),
                    ("state", "in", absent_states),
                ],
                order="start_time desc",
                limit=1,
            )
        )
        if not_attended_shift:
            url = "/my/shift/solidarity/request/%i/%s" % (
                not_attended_shift.task_template_id.id,
                not_attended_shift.start_time,
            )
            return request.redirect(url)
        else:
            request.session["error_message"] = _("No absent shift was found")
            return request.redirect("/my/shift")

    @http.route(
        "/my/shift/solidarity/request/<int:template_id>/<string:date>",
        auth="user",
        website=True,
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

    @http.route("/my/shift/solidarity/request", auth="user", website=True)
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
            if "template_id" not in request.session or "date" not in request.session:
                return request.render(
                    "beesdoo_website_shift_swap.website_shift_swap_parameters_missing"
                )
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
            if regular and non_realisable_tmpl_dated.date > datetime.now():
                request.session["success_message"] = _(
                    "You have been unsubscribed from your shift. "
                    "Your counter will not be decreased."
                )
                # Clear session
                del request.session["template_id"]
                del request.session["date"]
            else:
                request.session["success_message"] = _(
                    "Your request has been taken into account. "
                    "Your counter has been incremented."
                )

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
        auth="user",
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

        # Check if the user is the owner of the request
        user = request.env["res.users"].sudo().browse(request.uid)
        if solidarity_request.worker_id.id != user.partner_id.id:
            raise Forbidden("You are not allowed to cancel this request")

        if solidarity_request.cancel_solidarity_request():
            if (
                solidarity_request.worker_id.working_mode == "regular"
                and solidarity_request.tmpl_dated_id.date
                > solidarity_request.create_date
            ):
                request.session["success_message"] = _(
                    "You have successfully cancelled your solidarity request. "
                    "You have been subscribed back to your shift."
                )
            else:
                request.session["success_message"] = _(
                    "You have successfully cancelled your solidarity request. "
                    "Your counter has been decremented."
                )
        else:
            request.session["error_message"] = _(
                "You can't cancel this solidarity request."
            )
        return request.redirect("/my/shift")

    @http.route("/mail/toggle/exchanges", auth="user", website=True)
    def toggle_mail_exchange_subscription(self):
        if not self.exchanges_enabled():
            raise Forbidden("Shift exchanges are not enabled")

        worker = request.env["res.users"].sudo().browse(request.uid).partner_id

        is_subscribed = worker.subscribed_exchange_emails
        worker.subscribed_exchange_emails = not is_subscribed

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_toggle_email_exchanges",
            {"is_subscribed": is_subscribed},
        )

    def my_shift_next_shifts(self, partner=None):
        """
        Override my_shift_next_shifts method to sort shifts by date
        after taking into account exchanges and solidarity
        """
        res = super(WebsiteShiftSwapController, self).my_shift_next_shifts(partner)
        if self.solidarity_enabled() or self.exchanges_enabled():
            sorted_shifts = sorted(res["subscribed_shifts"], key=lambda r: r.start_time)
            res["subscribed_shifts"] = sorted_shifts
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
            "week_days": self.get_week_days(),
        }
