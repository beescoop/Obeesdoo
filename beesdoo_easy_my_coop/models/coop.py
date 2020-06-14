from odoo import api, models


class SubscriptionRequest(models.Model):
    _inherit = "subscription.request"

    _majority = 18

    def get_eater_vals(self, partner, share_product_id):
        vals = {}
        eater = share_product_id.eater

        if partner.is_company or partner.age < self._majority:
            eater = "eater"

        vals["eater"] = eater

        return vals

    @api.multi
    def validate_subscription_request(self):
        self.ensure_one()

        invoice = super(
            SubscriptionRequest, self
        ).validate_subscription_request()[0]
        partner = invoice.partner_id

        vals = self.get_eater_vals(partner, self.share_product_id)
        partner.write(vals)

        return invoice
