# -*- coding: utf-8 -*-

# Copyright 2019-2020 Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class ShiftConfigSettings(models.TransientModel):
    _name = "beesdoo.shift.config.settings"
    _inherit = "res.config.settings"

    default_task_type_id = fields.Many2one(
        "beesdoo.shift.type",
        string="Default Task Type",
        help="Default task type for shifts added on an attendance sheet.",
    )

    @api.multi
    def set_params(self):
        self.ensure_one()
        value = self.default_task_type_id.id
        parameters = self.env["ir.config_parameter"]
        parameters.set_param("beesdoo_shift.default_task_type_id", value)

    @api.multi
    def get_default_task_type_id(self):
        return {
            "default_task_type_id": int(
                self.env["ir.config_parameter"].get_param(
                    "beesdoo_shift.default_task_type_id"
                )
            )
        }
