from odoo import fields, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    template_structure = fields.Many2one(
        "res.partner",
        related="task_template_id.structure",
        store=True,
    )
