from odoo import api, fields, models


class Volunteer(models.Model):
    _name = "volunteer.volunteer"
    _description = "Volunteer"
    _inherits = {"res.partner": "partner_id"}
    _inherit = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one(
        "res.partner", delegate=True, ondelete="cascade", required=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
    shift_participation_ids = fields.Many2many(
        "volunteer.shift", string="Participations"
    )
    is_regular = fields.Boolean(
        compute="_compute_is_regular", precompute=True, store=True
    )

    # Compute test on participation before final implementation on subscription
    @api.depends("shift_participation_ids")
    def _compute_is_regular(self):
        for volunteer in self:
            if len(volunteer.shift_participation_ids) == 0:
                volunteer.is_regular = False
            else:
                volunteer.is_regular = True
