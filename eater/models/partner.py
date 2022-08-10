# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    eater = fields.Selection(
        [("eater", "Eater"), ("worker_eater", "Worker and Eater")],
        string="Eater/Worker",
    )
    child_eater_ids = fields.One2many(
        "res.partner",
        "parent_eater_id",
        domain=[("customer", "=", True), ("eater", "=", "eater")],
    )
    parent_eater_id = fields.Many2one(
        "res.partner", string="Parent Worker", readonly=True
    )

    @api.multi
    def write(self, values):
        for partner in self:
            if (
                values.get("parent_eater_id")
                and partner.parent_eater_id
                and partner.parent_eater_id.id != values.get("parent_eater_id")
            ):
                raise ValidationError(
                    _(
                        "You try to assign a eater to a partner but this eater "
                        "is already assign to %s please remove it before "
                    )
                    % partner.parent_eater_id.name
                )
        # replace many2many command when writing on child_eater_ids to just
        # remove the link
        if "child_eater_ids" in values:
            for command in values["child_eater_ids"]:
                if command[0] == 2:
                    command[0] = 3
        return super(Partner, self).write(values)

    @api.multi
    def _new_eater(self, surname, name, email):
        partner_data = {
            "lastname": name,
            "firstname": surname,
            "customer": True,
            "eater": "eater",
            "parent_eater_id": self.id,
            "email": email,
            "country_id": self.country_id.id,
        }
        return self.env["res.partner"].create(partner_data)
