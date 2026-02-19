# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import fields, models


class VolunteerShiftRecurrentGenerator(models.Model):
    _inherit = "volunteer.shift.recurrent.generator"

    is_maintained_during_holiday = fields.Boolean("Maintain During Holidays")
