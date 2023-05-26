import logging

from odoo import http
from odoo.http import request

from odoo.addons.shift_portal.controllers.main import WebsiteShiftController

_logger = logging.getLogger(__name__)


class WebsiteShiftController(WebsiteShiftController):
    def compute_display_shift(self, free_space, task_template):
        res = super().compute_display_shift(free_space, task_template)
        selected_beneficiary = self.get_selected_beneficiary()
        if selected_beneficiary:
            res = res and task_template.beneficiary == selected_beneficiary
        return res

    def get_selected_beneficiary(self):
        try:
            beneficiary_id = int(request.session.get("beneficiary", 0))
        except ValueError:
            beneficiary_id = 0
        return request.env["res.partner"].browse(beneficiary_id).exists()

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
            try:
                # Make sure beneficiary is parseable as int.
                value = kw.get("beneficiary")
                request.session["beneficiary"] = str(int(value))
            except ValueError:
                _logger.warning(
                    "keyword 'beneficiary' in '/shift_irregular_worker' was not"
                    " parseable as int: %s",
                    value,
                )
        return super().public_shift_irregular_worker()
