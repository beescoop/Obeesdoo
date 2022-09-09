# Copyright 2019 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

_MAJORITY = 18


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

    def get_eater_vals(self, partner, share_product_id):
        eater = share_product_id.eater

        # if birthdate_date is not set, age is 0 and lower than _MAJORITY
        # in that case, the configuration coming from the share product is kept
        if partner.is_company or (partner.birthdate_date and partner.age < _MAJORITY):
            eater = "eater"

        return {"eater": eater}

    @api.multi
    def validate_subscription_request(self):
        self.ensure_one()

        invoice = super().validate_subscription_request()[0]
        partner = invoice.partner_id

        vals = self.get_eater_vals(partner, self.share_product_id)
        partner.write(vals)

        return invoice
