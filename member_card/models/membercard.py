import uuid

from odoo import fields, models


class MemberCard(models.Model):
    def _get_current_user(self):
        return self.env.uid

    def _compute_bar_code(self):
        rule = self.env["barcode.rule"].search([("name", "=", "Customer Barcodes")])[0]
        size = 13 - len(rule.pattern)
        ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
        return ean[0:12] + str(self.env["barcode.nomenclature"].ean_checksum(ean))

    _name = "member.card"
    _order = "create_date desc"
    _description = "Member Card"

    valid = fields.Boolean(default=True, string="Active")
    barcode = fields.Char("Barcode", oldname="ean13", default=_compute_bar_code)
    partner_id = fields.Many2one("res.partner")  # , default=_get_current_client)
    responsible_id = fields.Many2one(
        "res.users", default=_get_current_user, string="Responsible"
    )
    end_date = fields.Date(readonly=True, string="Expiration Date")
    comment = fields.Char("Reason", required=True)
