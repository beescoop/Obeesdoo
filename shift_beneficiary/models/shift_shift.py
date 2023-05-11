from odoo import fields, models


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    template_beneficiary = fields.Many2one(
        "res.partner",
        related="task_template_id.beneficiary",
        store=True,
    )
