from datetime import datetime

from werkzeug.exceptions import Forbidden

from odoo import _, http
from odoo.http import request

from odoo.addons.beesdoo_website_shift.controllers.main import WebsiteShiftController


class WebsiteShiftCommitteeController(WebsiteShiftController):
    # Override /my/shift webpage controller
    @http.route("/my/shift", auth="user", website=True)
    def my_shift(self, **kw):
        res = super(WebsiteShiftCommitteeController, self).my_shift()
        template_context = res.qcontext

        template_context["request_committee"] = False
        if "request_committee" in kw:
            template_context["request_committee"] = kw["request_committee"]

        return request.render(res.template, template_context)

    @http.route("/my/shift/request/committee/<int:shift_id>", auth="user", website=True)
    def request_committee_shift(self, shift_id, **post):
        user = request.env["res.users"].sudo().browse(request.uid)
        asked_shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)
        if asked_shift.worker_id.id != user.partner_id.id:
            raise Forbidden(
                "You can't make this request on a shift you are not working on"
            )

        if request.httprequest.method == "POST":
            reason = request.httprequest.form.get("reason")

            mail_template = request.env.ref(
                "beesdoo_website_shift_committee.request_committee_shift"
            ).sudo()
            email_to = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("validating_user_email")
            )
            email_values = {
                "email_to": email_to,
                "reason": reason,
                "shift": asked_shift,
            }
            mail_template.with_context(email_values).send_mail(user.partner_id.id)

            request.session["success_message"] = _(
                "Your request has been handed over to the members office. "
                "You will be notified by email if they accept it."
            )
            return request.redirect("/my/shift")

        return request.render("beesdoo_website_shift_committee.request_committee_shift")

    @http.route(
        "/validate/committee/<int:worker_id>/<int:shift_id>", auth="user", website=True
    )
    def validate_committee_shift(self, worker_id, shift_id):
        # Check current user rights
        cur_user = request.env["res.users"].sudo().browse(request.uid)
        if not cur_user.has_group("beesdoo_shift.group_shift_management"):
            raise Forbidden("You don't have the right to perform this operation")

        asking_worker = request.env["res.partner"].sudo().browse(worker_id)
        asked_shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)

        if (
            asked_shift
            and asked_shift.worker_id.id == asking_worker.id
            and asked_shift.start_time > datetime.now()
        ):
            asked_shift.write(
                {
                    "is_regular": False,
                    "is_compensation": False,
                    "worker_id": False,
                }
            )
            mail_template = request.env.ref(
                "beesdoo_website_shift_committee.committee_shift_confirmation"
            ).sudo()
            email_values = {
                "partner_to": asking_worker,
                "shift": asked_shift,
            }
            mail_template.with_context(email_values).send_mail(cur_user.partner_id.id)
            return request.render(
                "beesdoo_website_shift_committee.validate_request_success"
            )

        return request.render("beesdoo_website_shift_committee.validate_request_error")
