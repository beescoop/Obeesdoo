# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import Form, SavepointCase


class MemberCardCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")

    def _new_card_wizard(self, partner, new_comment, force_barcode=None):
        ctx = {"active_id": partner.id}
        with Form(
            self.env["new.member.card.wizard"].with_context(**ctx)
        ) as wizard_form:
            wizard_form.new_comment = new_comment
            wizard_form.force_barcode = force_barcode
            wizard = wizard_form.save()
        wizard.create_new_card()
        return wizard

    def test_member_card_generate_barcode(self):
        self._new_card_wizard(
            self.partner,
            new_comment="new card",
        )

        member_card = self.partner.member_card_ids
        self.assertTrue(member_card)
        self.assertTrue(self.partner.barcode)
        self.assertEqual(member_card.barcode, self.partner.barcode)

    def test_member_card_force_barcode(self):
        barcode = "987654321"
        self._new_card_wizard(
            self.partner,
            new_comment="force barcode",
            force_barcode=barcode,
        )

        member_card = self.partner.member_card_ids
        self.assertEqual(member_card.barcode, barcode)
        self.assertEqual(member_card.barcode, self.partner.barcode)

    def test_second_card_invalidates_first(self):
        self._new_card_wizard(
            self.partner,
            new_comment="force barcode",
        )

        first_card = self.partner.member_card_ids
        self._new_card_wizard(
            self.partner,
            new_comment="force barcode",
        )
        self.assertEqual(len(self.partner.member_card_ids), 2)
        # have to use id to sort because both create_date are
        # too close and sometimes equal
        second_card = self.partner.member_card_ids.sorted(
            lambda mc: mc.id, reverse=True
        )[0]
        self.assertFalse(first_card.valid)
        self.assertEqual(first_card.end_date, fields.Date.today())
        self.assertTrue(second_card.valid)
        self.assertEqual(second_card.barcode, self.partner.barcode)
