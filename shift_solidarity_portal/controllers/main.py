# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from werkzeug.exceptions import Forbidden

from odoo import _, http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.beesdoo_website_shift.controllers.main import WebsiteShiftController


class ShiftSolidarityPortal(WebsiteShiftController):
    def is_solidarity_enabled(self):
        return bool(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("shift_solidarity.enable_solidarity")
        )

    def get_solidarity_counter_limit(self):
        try:
            solidarity_counter_limit = int(
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("shift_solidarity.solidarity_counter_limit")
            )
        except ValueError:
            solidarity_counter_limit = 0
        return solidarity_counter_limit

    # Override /my/shift webpage controller
    @http.route("/my/shift", auth="user", website=True)
    def my_shift(self, **kw):
        res = super().my_shift(**kw)
        template_context = res.qcontext
        template_context["is_solidarity_enabled"] = self.is_solidarity_enabled()
        template_context["is_solidarity_counter_ok"] = (
            request.env["res.company"]._company_default_get().solidarity_counter()
            > self.get_solidarity_counter_limit()
        )
        template_context["solidarity_counter"] = (
            request.env["res.company"]._company_default_get().solidarity_counter()
        )
        return request.render(res.template, template_context)

    # Solidarity shift offer
    @http.route("/my/shift/solidarity/offer/select", auth="user", website=True)
    def select_shift_solidarity_offer(self, **kw):
        """Page to choose a shift to subscribe for solidarity"""
        if not self.is_solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        error = None
        if request.httprequest.method == "POST":
            try:
                shift_id = int(kw.get("shift_id"))
                shift = request.env["shift.shift"].sudo().browse(shift_id).exists()
            except ValueError:
                shift = None

            try:
                if not shift:
                    raise UserError(_("The selected shift does not exists."))
                # we need a savepoint to have the same behavoir than in
                # backend.
                with request.env.cr.savepoint():
                    request.env["shift.solidarity.offer"].sudo().create(
                        {
                            "worker_id": request.env.user.partner_id.id,
                            "shift_id": shift.id,
                            "state": "validated",
                        }
                    )
            except (UserError, ValidationError) as err:
                error = err.name
            else:
                return request.redirect("/my/shift")

        irregular_enable_sign_up = False
        nexturl = "/my/shift"
        qcontext = {
            "solidarity_offer_enabled": True,
            "error": error,
        }
        qcontext.update(
            self.available_shift_irregular_worker(
                shift_domain=request.env["shift.solidarity.offer"]
                .sudo()
                ._get_shift_domain(),
                irregular_enable_sign_up=irregular_enable_sign_up,
                nexturl=nexturl,
            )
        )

        return request.render(
            "shift_solidarity_portal.shift_solidarity_offer_selection",
            qcontext,
        )

    @http.route(
        "/my/shift/solidarity/offer/cancel/<int:solidarity_offer_id>",
        auth="user",
        website=True,
    )
    def cancel_shift_solidarity_offer(self, solidarity_offer_id, **kw):
        if not self.is_solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        offer = (
            request.env["shift.solidarity.offer"]
            .sudo()
            .browse(solidarity_offer_id)
            .exists()
        )
        error = None
        try:
            # Check if the user is the owner of the offer
            if not offer or offer.worker_id != request.env.user.partner_id:
                raise UserError(_("You are not allowed to cancel this offer."))
            # we need a savepoint to have the same behavoir than in
            # backend.
            with request.env.cr.savepoint():
                offer.state = "cancelled"
        except (UserError, ValidationError) as err:
            error = err.name

        return request.render(
            "shift_solidarity_portal.shift_solidarity_offer_cancel",
            {"error": error},
        )

    @http.route("/my/shift/solidarity/request/select", auth="user", website=True)
    def select_shift_solidarity_request(self, **kw):
        if not self.is_solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        error = None
        if request.httprequest.method == "POST":
            try:
                shift_id = int(kw.get("shift_id"))
                shift = request.env["shift.shift"].sudo().browse(shift_id).exists()
            except ValueError:
                shift = None

            try:
                if not shift:
                    raise UserError(_("The selected shift does not exists."))
                # we need a savepoint to have the same behavoir than in
                # backend.
                with request.env.cr.savepoint():
                    request.env["shift.solidarity.request"].sudo().create(
                        {
                            "worker_id": request.env.user.partner_id.id,
                            "shift_id": shift.id,
                            "reason": kw.get("reason"),
                            "state": "validated",
                        }
                    )
            except (UserError, ValidationError) as err:
                error = err.name
            else:
                return request.redirect("/my/shift")

        shifts = (
            request.env["shift.shift"]
            .sudo()
            .search(
                request.env["shift.solidarity.request"]
                .sudo()
                ._get_shift_domain(request.env.user.partner_id),
                order="start_time desc",
            )
        )

        qcontext = {
            "error": error,
            "shifts": shifts,
        }

        return request.render(
            "shift_solidarity_portal.shift_solidarity_request_selection",
            qcontext,
        )

    @http.route("/my/shift/solidarity/requests", auth="user", website=True)
    def list_shift_solidarity_request(self, **kw):
        if not self.is_solidarity_enabled():
            raise Forbidden("Solidarity related features are not enabled")

        error = None
        success = None
        if request.httprequest.method == "POST":
            try:
                solidarity_request_id = int(kw.get("solidarity_request_id"))
                solidarity_request = (
                    request.env["shift.solidarity.request"]
                    .sudo()
                    .browse(solidarity_request_id)
                    .exists()
                )
            except ValueError:
                solidarity_request = None

            try:
                if not solidarity_request:
                    raise UserError(
                        _("The selected solidarity request does not exists.")
                    )
                # We need a savepoint to have the same behavoir than in
                # backend.
                with request.env.cr.savepoint():
                    solidarity_request.write(
                        {
                            "state": kw.get("state"),
                        }
                    )
            except (UserError, ValidationError) as err:
                error = err.name
            else:
                success = _(
                    "Your solidarity request has successfully " "been cancelled."
                )

        solidarity_requests = (
            request.env["shift.solidarity.request"]
            .sudo()
            .search(
                [("worker_id", "=", request.env.user.partner_id.id)],
                order="create_date desc",
            )
        )

        qcontext = {
            "error": error,
            "success": success,
            "solidarity_requests": solidarity_requests,
        }

        return request.render(
            "shift_solidarity_portal.list_solidarity_requests",
            qcontext,
        )
