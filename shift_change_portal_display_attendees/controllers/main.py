# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo.http import request

from odoo.addons.shift_change_portal.controllers.main import ShiftChangePortal


class ShiftChangePortalDisplayAttendees(ShiftChangePortal):
    def choose_new_shift(self, old_shift_id, **kw):
        res = super().choose_new_shift(old_shift_id, **kw)

        # Inject display_attendees into the template context
        if hasattr(res, "qcontext"):
            res.qcontext[
                "display_attendees"
            ] = request.website.display_attendees_on_portal

        return res
