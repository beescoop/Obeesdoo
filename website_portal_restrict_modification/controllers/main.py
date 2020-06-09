# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans  <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalRestrictModification(CustomerPortal):
    # override from `portal` module
    CustomerPortal.MANDATORY_BILLING_FIELDS = [
        "city",
        "country_id",
        "phone",
        "street",
        "zipcode",
    ]
    CustomerPortal.OPTIONAL_BILLING_FIELDS = ["state_id"]

    def details_form_validate(self, data):
        error, error_message = super().details_form_validate(data)

        # since we override mandatory and optional billing fields,
        # parent method will insert the following key/value in `error` dict and `error_message` list,
        # preventing from saving the form. Workaround is to remove them from both dict and list.
        if (
            error.get("common")
            and error["common"].lower() == "unknown field"
            and any("unknown field" in s.lower() for s in error_message)
        ):
            error.pop("common")
            error_message = [s for s in error_message if "unknown field" not in s.lower()]

        return error, error_message
