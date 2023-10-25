from odoo import models

_MAJORITY = 18


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    def get_eater_vals(self, partner, share_product_id):
        eater = share_product_id.eater

        # if birthdate_date is not set, age is 0 and lower than _MAJORITY
        # in that case, the configuration coming from the share product is kept
        if partner.is_company or (partner.birthdate_date and partner.age < _MAJORITY):
            eater = "eater"

        return {"eater": eater}

    def validate_subscription_request(self):
        self.ensure_one()

        invoice = super().validate_subscription_request()[0]
        partner = invoice.partner_id

        vals = self.get_eater_vals(partner, self.share_product_id)
        partner.write(vals)

        return invoice
