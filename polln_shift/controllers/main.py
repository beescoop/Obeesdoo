from werkzeug.exceptions import Forbidden

from odoo import http
from odoo.http import request


class WebsiteMacavracShiftController(http.Controller):
    @http.route("/shift/<int:shift_id>/unsubscribe", auth="user", website=True)
    def unsubscribe_to_shift(self, shift_id=-1, **kw):
        shift = request.env["beesdoo.shift.shift"].sudo().browse(shift_id)
        # Get current user
        if request.env.user.partner_id != shift.worker_id or not shift.can_unsubscribe:
            raise Forbidden()
        shift.worker_id = False
        return request.redirect(kw["nexturl"])
