# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShift(models.Model):
    _inherit = "volunteer.shift"

    shift_constrain_id = fields.Many2one(
        string="Constrain",
        comodel_name="volunteer.shift.constrain",
    )
    is_constrain_satisfied = fields.Boolean(
        compute="_compute_is_constrain_satisfied", store=True
    )

    def _compute_is_constrain_satisfied(self):
        for shift in self:
            constrain = (
                shift.shift_constrain_id
                if shift.shift_constrain_id
                else shift.type_id.shift_constrain_id
            )
            satisfy_constrain = True
            for rule in constrain.skill_category_rule_ids:
                if not satisfy_constrain:
                    break
                satisfy_constrain = shift.volunteer_ids.filtered(
                    lambda rec: rule.skill_category_id in rec.skill_ids.category_ids
                )
            for rule in constrain.skill_rule_ids:
                if not satisfy_constrain:
                    break
                satisfy_constrain = shift.volunteer_ids.filtered(
                    lambda rec: rule.skill_id in rec.skill_ids
                )
            shift.is_constrain_satisfied = bool(satisfy_constrain)
