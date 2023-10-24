from odoo import fields, models


class NewEaterWizard(models.TransientModel):
    """
    A transient model for the creation of a eater related to a worker.
    """

    _name = "new.eater.wizard"
    _description = "Add an eater to the current partner"

    def _get_default_partner(self):
        return self.env.context["active_id"]

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char()

    partner_id = fields.Many2one("res.partner", default=_get_default_partner)

    def create_new_eater(self):
        self.ensure_one()
        self.partner_id._new_eater(self.first_name, self.last_name, self.email)
