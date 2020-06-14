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
    barcode = fields.Char(
        compute="_get_bar_code", string="Barcode", store=True
    )
    parent_barcode = fields.Char(
        compute="_get_bar_code", string="Parent Barcode", store=True
    )
    member_card_ids = fields.One2many("member.card", "partner_id")

    member_card_to_be_printed = fields.Boolean("Print BEES card?")
    last_printed = fields.Datetime("Last printed on")

    @api.depends(
        "parent_eater_id",
        "parent_eater_id.barcode",
        "eater",
        "member_card_ids",
    )
    def _get_bar_code(self):
        for rec in self:
            if rec.eater == "eater":
                rec.parent_barcode = rec.parent_eater_id.barcode
            elif rec.member_card_ids:
                for c in rec.member_card_ids:
                    if c.valid:
                        rec.barcode = c.barcode

    @api.multi
    def write(self, values):
        for rec in self:
            if (
                values.get("parent_eater_id")
                and rec.parent_eater_id
                and rec.parent_eater_id.id != values.get("parent_eater_id")
            ):
                raise ValidationError(
                    _(
                        "You try to assign a eater to a worker but this eater is already assign to %s please remove it before"
                    )
                    % rec.parent_eater_id.name
                )
        # replace many2many command when writing on child_eater_ids to just remove the link
        if "child_eater_ids" in values:
            for command in values["child_eater_ids"]:
                if command[0] == 2:
                    command[0] = 3
        return super(Partner, self).write(values)

    def _deactivate_active_cards(self):
        self.ensure_one()
        for card in self.member_card_ids.filtered("valid"):
            card.valid = False
            card.end_date = fields.Date.today()

    @api.multi
    def _new_card(self, reason, user_id, barcode=False):
        card_data = {
            "partner_id": self.id,
            "responsible_id": user_id,
            "comment": reason,
        }
        if barcode:
            card_data["barcode"] = barcode
        self.env["member.card"].create(card_data)

    @api.multi
    def _new_eater(self, surname, name, email):
        partner_data = {
            "lastname": name,
            "firstname": surname,
            "is_customer": True,
            "eater": "eater",
            "parent_eater_id": self.id,
            "email": email,
            "country_id": self.country_id.id,
        }
        return self.env["res.partner"].create(partner_data)
