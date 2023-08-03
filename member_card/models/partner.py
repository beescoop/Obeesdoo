# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    barcode = fields.Char(
        compute="_compute_bar_code",
        # It makes no sense to keep this field company-dependent in this module.
        # Partners typically have no company. We could add a company field to
        # member.card and check it against the env's company to compute the
        # correct barcode. This would work, but means we can't use `store=True`
        # on this field.
        company_dependent=False,
        store=True,
    )
    member_card_ids = fields.One2many("member.card", "partner_id")

    member_card_to_be_printed = fields.Boolean("Print Member card?")
    last_printed = fields.Datetime("Last printed on")

    @api.depends(
        "member_card_ids",
        "member_card_ids.barcode",
    )
    def _compute_bar_code(self):
        for partner in self:
            if partner.member_card_ids:
                for c in partner.member_card_ids:
                    if c.valid:
                        partner.barcode = c.barcode
            else:
                partner.barcode = False

    def _deactivate_active_cards(self):
        self.ensure_one()
        for card in self.member_card_ids.filtered("valid"):
            card.valid = False
            card.end_date = fields.Date.today()

    def _new_card(self, reason, user_id, barcode=False):
        card_data = {
            "partner_id": self.id,
            "responsible_id": user_id,
            "comment": reason,
        }
        if barcode:
            card_data["barcode"] = barcode
        self.env["member.card"].create(card_data)
