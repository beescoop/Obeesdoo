# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class VolunteerVolunteer(models.Model):
    _inherit = "volunteer.volunteer"

    volunteer_leave_ids = fields.One2many(
        comodel_name="volunteer.volunteer.leave",
        inverse_name="volunteer_id",
        string="Leave",
    )

    def _send_notification_end_leave(self):
        """Send a notification to volunteers before their leave ends."""
        all_companies = self.env["res.company"].search([])
        for company in all_companies:
            nb_days = company.nb_days_before_leave_end
            message_body = ("Your leave ends in {} days.").format(nb_days)
            ending_soon_leaves = self.env["volunteer.volunteer.leave"].search(
                [
                    ("company_id", "=", company.id),
                    (
                        "end_date",
                        "=",
                        datetime.today().date() + relativedelta(days=nb_days),
                    ),
                ]
            )
            for leave in ending_soon_leaves:
                leave.volunteer_id.message_post(body=message_body)
