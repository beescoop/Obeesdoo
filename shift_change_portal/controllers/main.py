# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from werkzeug.exceptions import Forbidden, NotFound

from odoo import http
from odoo.exceptions import UserError, ValidationError
from odoo.http import request

from odoo.addons.beesdoo_website_shift.controllers.main import WebsiteShiftController


class ShiftChangePortal(WebsiteShiftController):
    def is_shift_change_enabled(self):
        # Warning! This will return True if the parameter is "False".
        # We find same issue in other Odoo config, so I preserve the
        # same behaviour here.
        return bool(
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("shift_change_portal.enable_shift_change")
        )

    @http.route()
    def my_shift(self, **kw):
        res = super().my_shift(**kw)
        qcontext = res.qcontext

        qcontext["is_shift_change_enabled"] = self.is_shift_change_enabled()

        return request.render(res.template, qcontext)

    @http.route("/my/shift/change/<int:old_shift_id>", auth="user", website=True)
    def choose_new_shift(self, old_shift_id, **kw):
        if not self.is_shift_change_enabled():
            raise Forbidden("Shift changes are not enabled")

        old_shift = request.env["shift.shift"].sudo().browse(old_shift_id).exists()
        if not old_shift:
            raise NotFound

        error = None
        try:
            request.env["shift.change"].sudo()._check_old_shift(
                old_shift, request.env.user.partner_id
            )
        except (UserError, ValidationError) as err:
            error = err.name

        irregular_enable_sign_up = False
        nexturl = "/my/shift"
        qcontext = {
            "regular_shift_change_enabled": True,
            "old_shift": old_shift,
            "error": error,
        }
        qcontext.update(
            self.available_shift_irregular_worker(
                shift_domain=request.env["shift.change"].sudo()._get_new_shift_domain(),
                irregular_enable_sign_up=irregular_enable_sign_up,
                nexturl=nexturl,
            )
        )

        return request.render(
            "shift_change_portal.shift_change_selection",
            qcontext,
        )

    @http.route(
        "/my/shift/change/<int:old_shift_id>/<int:new_shift_id>",
        auth="user",
        website=True,
    )
    def validate_change(self, old_shift_id, new_shift_id, **kw):
        if not self.is_shift_change_enabled():
            raise Forbidden("Shift changes are not enabled")

        old_shift = request.env["shift.shift"].browse(old_shift_id).exists().sudo()
        new_shift = request.env["shift.shift"].browse(new_shift_id).exists().sudo()
        if not old_shift or not new_shift:
            raise NotFound

        error = None
        if request.httprequest.method == "POST":
            try:
                # We need that the create rollback in case of an error.
                # In a controller is not the default as in wizards.
                # So we manually create a savepoint before calling the
                # create.
                with request.env.cr.savepoint():
                    request.env["shift.change"].sudo().create(
                        {
                            "worker_id": request.env.user.partner_id.id,
                            "old_shift_id": old_shift.id,
                            "new_shift_id": new_shift.id,
                        }
                    )
            except (UserError, ValidationError) as err:
                error = err.name
            else:
                return request.redirect("/my/shift")

        qcontext = {
            "error": error,
            "old_shift": old_shift,
            "new_shift": new_shift,
        }
        return request.render("shift_change_portal.validate_change", qcontext)
