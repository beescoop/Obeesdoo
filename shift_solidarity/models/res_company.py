# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def _get_solidarity_counter_limit(self):
        """Return value for solidarity_counter_limit parameter"""
        try:
            solidarity_counter_limit = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("shift_solidarity.solidarity_counter_limit")
            )
        except ValueError:
            # fall back to a default value
            solidarity_counter_limit = 0
        return solidarity_counter_limit

    @api.model
    def solidarity_counter(self):
        """
        Calculate the value of the solidarity counter. The initial value is
        stored in parameter 'solidarity_counter_start_value'.
        :return: Integer
        """
        offers = self.env["shift.solidarity.offer"].search([])
        requests = self.env["shift.solidarity.request"].search(
            [("state", "=", "validated")]
        )
        try:
            start_value = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("shift_solidarity.solidarity_counter_start_value")
            )
        except ValueError:
            start_value = 0
        return start_value + offers.count_attended_solidarity_offers() - len(requests)

    @api.model
    def _check_counter_limit(self):
        solidarity_counter_limit = self._get_solidarity_counter_limit()
        counter = self.solidarity_counter()
        if counter < solidarity_counter_limit:
            raise ValidationError(
                _(
                    "The solidarity counter can not go below %s."
                    % solidarity_counter_limit
                )
            )
