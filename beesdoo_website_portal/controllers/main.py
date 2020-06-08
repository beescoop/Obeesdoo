# -*- coding: utf-8 -*-
# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans  <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.website_portal_extend.controllers.main import ExtendWebsiteAccountController
from odoo.http import request


class BeesdooAccountWebsiteController(ExtendWebsiteAccountController):

    mandatory_billing_fields = [
        "phone",
        "city",
        "country_id",
        "street",
        "zipcode",
    ]
    optional_billing_fields = [
        "state_id",
    ]

    def _set_mandatory_fields(self, data):
        """This is not useful as the field 'company_name' is not present
        anymore.
        """
        pass
