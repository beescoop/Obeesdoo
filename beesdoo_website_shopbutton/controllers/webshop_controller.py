# Copyright 2025 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request


class WebshopController(http.Controller):
    @http.route("/webshop_button", type="http", auth="user", website=True)
    def webshop_button_diy(self, **kwargs):

        user = request.env.user
        # TODO: error when not logged in?
        return request.redirect(user.webshop_url)
