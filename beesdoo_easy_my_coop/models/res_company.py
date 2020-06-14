# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"
    display_info_session_confirmation = fields.Boolean(
        help="Choose to display a info session checkbox on the cooperator"
        " website form."
    )
    info_session_confirmation_required = fields.Boolean(
        string="Is info session confirmation required?"
    )
    info_session_confirmation_text = fields.Html(
        translate=True,
        help="Text to display aside the checkbox to confirm"
        " participation to an info session.",
    )

    @api.onchange("info_session_confirmation_required")
    def onchange_info_session_confirmatio_required(self):
        if self.info_session_confirmation_required:
            self.display_info_session_confirmation = True

    _sql_constraints = [
        (
            "info_session_approval_constraint",
            """CHECK ((info_session_confirmation_required=FALSE
            AND display_info_session_confirmation=FALSE)
            OR display_info_session_confirmation=TRUE)
        """,
            "Approval can't be mandatory and not displayed.",
        )
    ]
