"""
Created on 2 janv. 2017

@author: Thibault Francois
"""

from odoo import _, api, fields, models


class GenerateShiftTemplate(models.TransientModel):
    _name = "beesddoo.shift.generate_shift_template"
    _description = "beesddoo.shift.generate_shift_template"

    day_ids = fields.Many2many(
        comodel_name="beesdoo.shift.daynumber",
        relation="template_gen_day_number_rel",
        column1="wizard_id",
        column2="day_id",
    )
    planning_ids = fields.Many2many(
        comodel_name="beesdoo.shift.planning",
        relation="generate_shift_planning_rel",
        column1="planning_id",
        column2="wizard_id",
        required=True,
    )
    type_id = fields.Many2one(
        "beesdoo.shift.type",
        default=lambda self: self._context.get("active_id"),
    )
    line_ids = fields.One2many(
        "beesddoo.shift.generate_shift_template.line", "wizard_id"
    )

    @api.multi
    def generate(self):
        self.ensure_one()
        ids = []
        for planning_id in self.planning_ids:
            for day in self.day_ids:
                for line in self.line_ids:
                    shift_template_data = {
                        "name": "%s" % self.type_id.name,
                        "planning_id": planning_id.id,
                        "task_type_id": self.type_id.id,
                        "day_nb_id": day.id,
                        "start_time": line.start_time,
                        "end_time": line.end_time,
                        "duration": line.end_time - line.start_time,
                        "worker_nb": line.worker_nb,
                    }
                    new_rec = self.env["beesdoo.shift.template"].create(
                        shift_template_data
                    )
                    ids.append(new_rec.id)
        return {
            "name": _("Generated Shift Template"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "kanban,tree,form",
            "res_model": "beesdoo.shift.template",
            "target": "current",
            "domain": [("id", "in", ids)],
            "context": {"group_by": "day_nb_id"},
        }


class GenerateShiftTemplateLine(models.TransientModel):
    _name = "beesddoo.shift.generate_shift_template.line"
    _description = "beesddoo.shift.generate_shift_template.line"

    wizard_id = fields.Many2one("beesddoo.shift.generate_shift_template")
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    worker_nb = fields.Integer(default=1)
