# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import api, fields, models


class Volunteer(models.Model):
    _name = "volunteer.volunteer"
    _description = "Volunteer"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # General fields

    is_regular = fields.Boolean(
        default=False,
        readonly=True,
        help="Is regular if registered for at least one recurrent shift",
    )

    # Relational fields

    partner_id = fields.Many2one(
        comodel_name="res.partner", delegate=True, ondelete="cascade", required=True
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.user.company_id,
        required=True,
        tracking=True,
    )
    shift_participation_ids = fields.One2many(
        comodel_name="volunteer.shift.participation",
        inverse_name="volunteer_id",
        string="Participation",
        tracking=True,
    )

    # Computed fields

    count_participation = fields.Integer(compute="_compute_count_participation")
    count_participation_future = fields.Integer(
        compute="_compute_count_participation_future"
    )

    # Compute methods

    @api.depends("shift_participation_ids")
    def _compute_count_participation_future(self):
        for volunteer in self:
            volunteer.count_participation_future = len(
                volunteer.shift_participation_ids.filtered(
                    lambda participation: participation.shift_id.start_time
                    >= fields.Datetime.now()
                )
            )

    @api.depends("shift_participation_ids")
    def _compute_count_participation(self):
        for volunteer in self:
            volunteer.count_participation = len(volunteer.shift_participation_ids)

    # Action methods

    def action_view_volunteer_shifts(self):
        """Open all shifts of the current volunteer."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "My Shifts",
            "res_model": "volunteer.shift",
            "view_mode": "kanban,tree,form",
            "domain": [("volunteer_ids", "in", [self.id])],
        }

    def action_view_volunteer_future_shifts(self):
        """Open the future shifts of the current volunteer."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "My Future Shifts",
            "res_model": "volunteer.shift",
            "view_mode": "kanban,tree,form",
            "domain": [("volunteer_ids", "in", [self.id])],
            "context": {"search_default_filter_future": 1},
        }
