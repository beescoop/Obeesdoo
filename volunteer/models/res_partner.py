from odoo import api, fields, models


class Partner(models.Model):
    _inherit = ["res.partner"]

    volunteer_ids = fields.One2many(
        "volunteer.volunteer", "partner_id", string="Volunteer"
    )

    is_regular = fields.Boolean(
        string="Regular Volunteer",
        compute="_compute_is_regular",
    )

    @api.depends("volunteer_ids")
    def _compute_is_regular(self):
        for partner in self:
            if partner.volunteer_ids:
                partner.is_regular = partner.volunteer_ids.is_regular
            else:
                partner.is_regular = False
