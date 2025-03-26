from odoo import fields, models


class ShiftStage(models.Model):
    _name = "volunteer.shift.stage"
    _description = "Shift Stage"
    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer(default=10)
    fold = fields.Boolean()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("canceled", "Canceled")],
        default="draft",
    )
