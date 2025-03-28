from odoo import fields, models


class CoordinatorLine(models.Model):
    """Coordinator Line used to bypass the inability to add records inline
    for a Many2many field in the notebook."""

    _name = "volunteer.coordinator.line"
    _description = "Coordinator Line"

    shift_id = fields.Many2one("volunteer.shift", required=True)
    coordinator_id = fields.Many2one("volunteer.volunteer", "Volunteer", required=True)
