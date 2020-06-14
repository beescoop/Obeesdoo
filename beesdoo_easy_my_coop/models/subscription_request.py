# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    info_session_confirmed = fields.Boolean(
        string="Confirmed Info Session", default=False
    )

    def get_partner_vals(self):
        partner_vals = super(SubscriptionRequest, self).get_partner_vals()
        partner_vals["info_session_confirmed"] = self.info_session_confirmed
        return partner_vals

    def get_required_field(self):
        required_fields = super(SubscriptionRequest, self).get_required_field()
        company = self.env["res.company"]._company_default_get()
        if company.info_session_confirmation_required:
            required_fields.append("info_session_confirmed")
        return required_fields
