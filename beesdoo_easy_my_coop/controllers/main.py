from odoo.http import request

from odoo.addons.easy_my_coop_website.controllers.main import (
    WebsiteSubscription as Base,
)


class WebsiteSubscription(Base):
    def fill_values(self, values, is_company, logged, load_from_user=False):
        values = super(WebsiteSubscription, self).fill_values(
            values, is_company, logged, load_from_user
        )
        cmp = request.env["res.company"]._company_default_get()
        values.update(
            {
                "display_info_session": cmp.display_info_session_confirmation,
                "info_session_required": cmp.info_session_confirmation_required,
                "info_session_text": cmp.info_session_confirmation_text,
            }
        )
        return values
