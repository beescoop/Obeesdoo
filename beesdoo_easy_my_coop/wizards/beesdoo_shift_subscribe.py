# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Subscribe(models.TransientModel):
    _inherit = "beesdoo.shift.subscribe"

    def _get_info_session_followed(self):
        """
        Check if the user has checked the info_session_confirmed in the
        form to become new cooperator.
        """
        followed = super(Subscribe, self)._get_info_session_followed()
        if not followed:
            return (
                self.env["res.partner"]
                .browse(self._context.get("active_id"))
                .info_session_confirmed
            )
        return followed

    info_session = fields.Boolean(default=_get_info_session_followed)
