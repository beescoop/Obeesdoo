# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans  <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging

from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class CustomerPortalRestrictModification(CustomerPortal):
    def __init__(self, *args, **kwargs):
        super().__init__()
        # Class scope is accessible throughout the server even on
        # odoo instances that do not install this module.

        # Therefore : bring back to instance scope if not already
        if "MANDATORY_BILLING_FIELDS" not in vars(self):
            self.MANDATORY_BILLING_FIELDS = (
                CustomerPortal.MANDATORY_BILLING_FIELDS.copy()
            )
        if "OPTIONAL_BILLING_FIELDS" not in vars(self):
            self.OPTIONAL_BILLING_FIELDS = (
                CustomerPortal.OPTIONAL_BILLING_FIELDS.copy()
            )

        # move name and email to optional
        if "name" in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.remove("name")
        if "name" not in self.OPTIONAL_BILLING_FIELDS:
            self.OPTIONAL_BILLING_FIELDS.append("name")

        if "email" in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.remove("email")
        if "email" not in self.OPTIONAL_BILLING_FIELDS:
            self.OPTIONAL_BILLING_FIELDS.append("email")

        # move zipcode to mandatory
        if "zipcode" in self.OPTIONAL_BILLING_FIELDS:
            self.OPTIONAL_BILLING_FIELDS.remove("zipcode")
        if "zipcode" not in self.MANDATORY_BILLING_FIELDS:
            self.MANDATORY_BILLING_FIELDS.append("zipcode")
