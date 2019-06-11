# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class ResCompany(models.Model):

    _inherit = 'res.company'
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
        " participation to an info session."
    )

    @api.onchange('info_session_confirmation_required')
    def onchange_info_session_confirmatio_required(self):
        if self.info_session_confirmation_required:
            self.display_info_session_confirmation = True
