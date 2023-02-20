from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class WorkerPortalAccount(CustomerPortal):
    def __init__(self, *args, **kwargs):
        super().__init__()
        if "OPTIONAL_BILLING_FIELDS" not in vars(self):
            self.OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS.copy()
        self.OPTIONAL_BILLING_FIELDS.extend(["share_supercoop_info"])

    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update(
            {
                "super": partner.super,
                "share_supercoop_info": partner.share_supercoop_info,
            }
        )
        return values
