from datetime import datetime

from odoo import http
from odoo.http import request

# from odoo.addons.beesdoo_shift.models.planning import float_to_time
from odoo.addons.beesdoo_website_shift.controllers.main import WebsiteShiftController


class WebsiteShiftSwapController(WebsiteShiftController):
    def shift_to_tmpl_dated(self, my_shift):
        list_shift = []
        list_shift.append(my_shift)
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .swap_shift_to_tmpl_dated(list_shift)
        )
        return my_tmpl_dated

    def new_tmpl_dated(self, template_id, date):
        tmpl_dated = request.env["beesdoo.shift.template.dated"].new()
        tmpl_dated.template_id = template_id
        tmpl_dated.date = date
        return tmpl_dated

    @http.route("/my/shift/swaping/<int:template_id>/<string:date>", website=True)
    def swaping_shift(self, template_id, date):
        now = datetime.now()
        shift_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        # save the swaping tmpl_dated in the user session
        request.session["template_id"] = template_id
        request.session["date"] = date

        delta = shift_date - now
        if delta.days <= int(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.day_limit_swap")
        ):
            return request.redirect("/my/shift/underpopulated/swap")
        else:
            return request.redirect("/my/shift/possible/match")

    @http.route("/my/shift/underpopulated/swap", website=True)
    def get_underpopulated_shift(self):
        """
        Personnal page to choose the underpopulated shift you want
        """
        # Get unwanted tmpl_dated save in the user session
        # Get template and date from session
        template_id = request.session["template_id"]
        date = request.session["date"]
        # create new tmpl_dated
        my_tmpl_dated = self.new_tmpl_dated(template_id, date)

        # get underpopulated shift
        my_available_shift = (
            request.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .get_underpopulated_shift()
        )

        # Get the user's future shifts
        user = request.env["res.users"].sudo().browse(request.uid)
        my_shifts = user.sudo().partner_id.my_next_shift()
        subscribed_shifts = []
        for rec in my_shifts:
            subscribed_shifts.append(rec)

        # Remove the already subscribed shifts from the propositions
        for available_shift in my_available_shift:
            for tmpl_dated in request.env[
                "beesdoo.shift.template.dated"
            ].swap_shift_to_tmpl_dated(subscribed_shifts):
                if available_shift.date == tmpl_dated.date:
                    my_available_shift -= available_shift

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_underpopulated_tmpl_dated",
            {
                "underpopulated_shift": my_available_shift,
                "exchanged_tmpl_dated": my_tmpl_dated,
            },
        )

    @http.route(
        "/my/shift/underpopulated/swap/subscribe/"
        "<int:template_wanted>/<string:date_wanted>",
        website=True,
    )
    def subscribe_to_underpopulated_swap(self, template_wanted, date_wanted):
        user = request.env["res.users"].browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_id,
                    "date": date,
                    "store": True,
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
                    "store": True,
                }
            )
        )
        data = {
            "date": datetime.date(datetime.now()),
            "worker_id": user.partner_id.id,
            "exchanged_tmpl_dated_id": my_tmpl_dated.id,
            "confirmed_tmpl_dated_id": tmpl_dated_wanted.id,
        }
        record = (
            request.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .create(data)
        )
        if record._compute_exchanged_already_generated():
            record.unsubscribe_shift()
        if record._compute_comfirmed_already_generated():
            record.subscribe_shift()
        return request.redirect("/my/shift")

    @http.route("/my/shift/possible/shift", website=True)
    def get_possible_shift(self, **post):
        template_id = request.session["template_id"]
        date = request.session["date"]
        # liste de dictionaire
        # enregistrer information
        # indentifier case coché avec index
        my_tmpl_dated = self.new_tmpl_dated(template_id, date)
        possible_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"].sudo().display_tmpl_dated()
        )

        # register into session
        tmpl_dated = []
        for rec in possible_tmpl_dated:
            tmpl_dated.append(
                {
                    "template_id": rec.template_id.id,
                    "date": rec.date,
                }
            )
        request.session["tmpl_dated_checked"] = tmpl_dated

        if request.httprequest.method == "POST":
            # une fois appuyer sur submit
            # TODO : first checkbox return 'on'
            tmpl_dated_index = request.httprequest.form.getlist("tmpl_dated_index")
            list_index = []
            for rec in tmpl_dated_index:
                list_index.append(int(rec))
            # if not len(list_index):
            #    raise ValidationError('Please choose at least one tmpl_dated')
            return request.render(
                "beesdoo_website_shift.my_shift_regular_worker",
                self.subscribe_request(list_index),
            )
        else:
            return request.render(
                "beesdoo_website_shift_swap.website_shift_swap_possible_tmpl_dated",
                {
                    "possible_tmpl_dated": possible_tmpl_dated,
                    "exchanged_tmpl_dated": my_tmpl_dated,
                },
            )

    def subscribe_request(self, list_index):
        user = request.env["res.users"].browse(request.uid)

        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_id,
                    "date": date,
                    "store": True,
                }
            )
        )

        tmpl_dated = request.session["tmpl_dated_checked"]
        asked_tmpl_dated = request.env["beesdoo.shift.template.dated"]
        for x in range(len(tmpl_dated)):
            for i in range(len(list_index)):
                if list_index[i] == x:
                    data = {
                        "date": tmpl_dated[x]["date"],
                        "template_id": tmpl_dated[x]["template_id"],
                        "store": True,
                    }
                    create_tmpl_dated = (
                        request.env["beesdoo.shift.template.dated"].sudo().create(data)
                    )
                    # request.env["beesdoo.shift.template.dated"].sudo().check_possibility_to_exchange(create_tmpl_dated,user.partner_id)
                    asked_tmpl_dated |= create_tmpl_dated
        data = {
            "request_date": datetime.date(datetime.now()),
            "worker_id": user.partner_id.id,
            "exchanged_tmpl_dated_id": my_tmpl_dated.id,
            "asked_tmpl_dated_ids": [(6, False, asked_tmpl_dated.ids)],
            "status": "no_match",
        }
        request.env["beesdoo.shift.exchange_request"].sudo().create(data)
        return self.my_shift_regular_worker()

    @http.route("/my/shift/matching/request")
    def my_match(self):
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        my_exchanges = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("worker_id", "=", cur_user.partner_id.id)])
        )
        matchs = request.env["beesdoo.shift.exchange_request"]
        for exchange in my_exchanges:
            matchs |= request.env["beesdoo.shift.exchange_request"].matching_request(
                exchange.asked_tmpl_dated_ids, exchange.exchanged_tmpl_dated_id
            )

        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_matching_request",
            {"matching_request": matchs},
        )

    @http.route("/my/shift/possible/match", website=True)
    def get_possible_match(self):
        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = self.new_tmpl_dated(template_id, date)
        possible_match = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .get_possible_match(my_tmpl_dated)
        )
        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_possible_match",
            {
                "possible_matches": possible_match,
                "exchanged_tmpl_dated": my_tmpl_dated,
            },
        )

    @http.route("/my/request", website=True)
    def my_request(self):
        # Get current user
        cur_user = request.env["res.users"].browse(request.uid)
        my_requests = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("worker_id", "=", cur_user.partner_id.id)])
        )
        list = []
        for rec in my_requests:
            list.append(
                {
                    "my_requests": rec,
                    "matching_request": request.env["beesdoo.shift.exchange_request"]
                    .sudo()
                    .matching_request(
                        rec.asked_tmpl_dated_ids, rec.exchanged_tmpl_dated_id
                    ),
                }
            )

        return request.render(
            "beesdoo_website_shift_swap.my_request",
            {
                "my_requests": list,
            },
        )

    @http.route(
        "/my/shift/validate/matching_request/<int:matching_request_id>", website=True
    )
    def validate_matching_request(self, matching_request_id):
        cur_user = request.env["res.users"].browse(request.uid)
        template_id = request.session["template_id"]
        date = request.session["date"]
        my_tmpl_dated = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_id,
                    "date": date,
                    "store": True,
                }
            )
        )
        matching_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("id", "=", matching_request_id)])
        )
        data = {
            "request_date": datetime.date(datetime.now()),
            "worker_id": cur_user.partner_id.id,
            "exchanged_tmpl_dated_id": my_tmpl_dated.id,
            "asked_tmpl_dated_ids": [
                (6, False, matching_request.exchanged_tmpl_dated_id.ids)
            ],
            "validate_request_id": matching_request_id,
            "status": "validate_match",
        }
        new_request = request.env["beesdoo.shift.exchange_request"].sudo().create(data)
        matching_request.write({"status": "has_match"})
        matching_request.sudo().send_mail_matching_request(new_request)
        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/validate/matching/validate/request/"
        "<int:my_request_id>/<string:match_request_id>",
        website=True,
    )
    def validate_matching_validate_request(self, my_request_id, match_request_id):
        request.env["res.users"].browse(request.uid)
        exchange_data = {
            "first_request_id": my_request_id,
            "second_request_id": match_request_id,
        }
        exchange = request.env["beesdoo.shift.exchange"].sudo().create(exchange_data)

        my_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("id", "=", my_request_id)])
        )
        match_request = (
            request.env["beesdoo.shift.exchange_request"]
            .sudo()
            .search([("id", "=", match_request_id)])
        )
        data = {
            "validate_request": match_request_id,
            "exchange_id": exchange.id,
            "status": "done",
        }
        my_request.write(data)
        match_request.write({"status": "done"})
        if request.env["beesdoo.shift.exchange"].sudo().is_shift_generated(my_request):
            request.env["beesdoo.shift.exchange"].sudo().subscribe_exchange_to_shift(
                my_request
            )
            exchange.write({"first_shift_status": True})
        if (
            request.env["beesdoo.shift.exchange"]
            .sudo()
            .is_shift_generated(match_request)
        ):
            request.env["beesdoo.shift.exchange"].sudo().subscribe_exchange_to_shift(
                match_request
            )
            exchange.write({"second_shift_status": True})
        return request.redirect("/my/shift")

    # Solidarity shift offer
    @http.route("/my/shift/solidarity/offer", website=True)
    def get_underpopulated_shift_for_solidarity(self):
        """
        Page to choose an underpopulated shift to subscribe for solidarity
        """
        # Get underpopulated shifts
        next_underpopulated_shifts = (
            request.env["beesdoo.shift.subscribed_underpopulated_shift"]
            .sudo()
            .get_underpopulated_shift()
        )

        # Get the user's future shifts
        user = request.env["res.users"].sudo().browse(request.uid)
        my_future_shifts = user.sudo().partner_id.my_next_shift()
        subscribed_shifts = []
        for rec in my_future_shifts:
            subscribed_shifts.append(rec)

        # Remove the already subscribed shifts from the propositions
        for available_shift in next_underpopulated_shifts:
            for tmpl_dated in request.env[
                "beesdoo.shift.template.dated"
            ].swap_shift_to_tmpl_dated(subscribed_shifts):
                if available_shift.date == tmpl_dated.date:
                    next_underpopulated_shifts -= available_shift

        return request.render(
            "beesdoo_website_shift_swap."
            "website_shift_swap_select_solidarity_underpopulated",
            {"underpopulated_shift": next_underpopulated_shifts},
        )

    @http.route(
        "/my/shift/solidarity/offer/select/<int:template_wanted>/<string:date_wanted>",
        website=True,
    )
    def subscribe_to_underpopulated_shift_for_solidarity(
        self, template_wanted, date_wanted
    ):
        user = request.env["res.users"].browse(request.uid)

        tmpl_dated_wanted = (
            request.env["beesdoo.shift.template.dated"]
            .sudo()
            .create(
                {
                    "template_id": template_wanted,
                    "date": date_wanted,
                    "store": True,
                }
            )
        )
        data = {
            "worker_id": user.partner_id.id,
            "tmpl_dated_id": tmpl_dated_wanted.id,
        }
        record = request.env["beesdoo.shift.solidarity.offer"].sudo().create(data)
        record._compute_shift_id()
        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/solidarity/offer/cancel/<int:solidarity_offer_id>",
        website=True,
    )
    def cancel_solidarity_offer(self, solidarity_offer_id):
        solidarity_offer = (
            request.env["beesdoo.shift.solidarity.offer"]
            .sudo()
            .search(
                [
                    ("id", "=", solidarity_offer_id),
                ],
                limit=1,
            )
        )
        if solidarity_offer.state == "validated":
            solidarity_offer.unsubscribe_shift()
        solidarity_offer.state = "cancelled"
        return request.redirect("/my/shift")

    @http.route(
        "/my/shift/solidarity/request/<int:template_id>/<string:date>", website=True
    )
    def prepare_request_solidarity_shift(self, template_id, date):
        request.session["template_id"] = template_id
        request.session["date"] = date
        return request.redirect("/my/shift/solidarity/request")

    @http.route("/my/shift/solidarity/request", website=True)
    def request_solidarity_shift(self, **post):
        template_id = request.session["template_id"]
        date = request.session["date"]

        if request.httprequest.method == "POST":
            user = request.env["res.users"].browse(request.uid)
            non_realisable_tmpl_dated = (
                request.env["beesdoo.shift.template.dated"]
                .sudo()
                .create(
                    {
                        "template_id": template_id,
                        "date": date,
                        "store": True,
                    }
                )
            )
            data = {
                "worker_id": user.partner_id.id,
                "tmpl_dated_id": non_realisable_tmpl_dated.id,
            }
            solidarity_request = (
                request.env["beesdoo.shift.solidarity.request"].sudo().create(data)
            )
            reason = request.httprequest.form.get("reason")
            solidarity_request.reason = reason
            solidarity_request._compute_shift_id()
            return request.redirect("/my/shift")

        tmpl_dated = self.new_tmpl_dated(template_id, date)
        return request.render(
            "beesdoo_website_shift_swap.website_shift_swap_request_solidarity",
            {
                "tmpl_dated": tmpl_dated,
            },
        )
