from odoo import http
from odoo.http import request

from odoo.addons.shift_portal.controllers.main import WebsiteShiftController


class WebsiteShiftController(WebsiteShiftController):
    def compute_display_shift(self, free_space, task_template):
        res = super().compute_display_shift(free_space, task_template)
        selected_beneficiary = self.get_selected_beneficiary()
        if selected_beneficiary:
            res = res and task_template.beneficiary == selected_beneficiary
        return res

    def get_selected_beneficiary(self):
        beneficiary_model = request.env["res.partner"]
        if "beneficiary" in request.session:  # a filter has been applied
            beneficiary_id = request.session["beneficiary"]
            if beneficiary_id:  # the filter is not empty
                return beneficiary_model.browse(int(beneficiary_id))
        return beneficiary_model

    def available_shift_irregular_worker(
        self,
        irregular_enable_sign_up=False,
        nexturl="",
    ):
        res = super().available_shift_irregular_worker(
            irregular_enable_sign_up, nexturl
        )
        beneficiary_list = (
            request.env["res.partner"].sudo().search([("is_beneficiary", "=", True)])
        )
        res.update({"beneficiary_list": beneficiary_list})
        res.update({"selected_beneficiary": self.get_selected_beneficiary()})
        return res

    @http.route("/shift_irregular_worker", auth="public", website=True)
    def public_shift_irregular_worker(self, **kw):
        if request.httprequest.method == "POST":
            request.session["beneficiary"] = kw["beneficiary"]
        return super().public_shift_irregular_worker()
