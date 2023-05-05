from urllib.parse import urljoin

from odoo import http
from odoo.http import request
from odoo.addons.shift_portal.controllers.main import WebsiteShiftController


class WebsiteShiftController(WebsiteShiftController):

    def compute_display_shift(self, free_space, task_template):
        res = super().compute_display_shift(free_space, task_template)
        selected_structure = self.get_selected_structure()
        if selected_structure:
            res = res and task_template.structure == selected_structure
        return res

    def get_selected_structure(self):
        structure_model = request.env["res.partner"]
        if "structure" in request.session: # a filter has been applied
            structure_id = request.session["structure"]
            if structure_id: # the filter is not empty
                return structure_model.browse(int(structure_id))
        return structure_model
                
    def available_shift_irregular_worker(
        self, irregular_enable_sign_up=False, nexturl="",
    ):
        res = super().available_shift_irregular_worker(irregular_enable_sign_up, nexturl)
        structure_list = request.env["res.partner"].search([("is_structure", "=", True)])
        res.update({"structure_list": structure_list})
        res.update({"selected_structure": self.get_selected_structure()})
        return res

    @http.route("/shift_irregular_worker", auth="public", website=True)
    def public_shift_irregular_worker(self, **kw):
        if request.httprequest.method == 'POST':
            request.session["structure"] = kw["structure"]
        return super().public_shift_irregular_worker()

