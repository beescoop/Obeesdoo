import uuid

from odoo import fields, models


class MemberCard(models.Model):
    _name = "member.card"
    _order = "create_date desc"
    _description = "Member Card"

    def _get_current_user(self):
        return self.env.uid

    def _compute_bar_code(self):
        ean = str(uuid.uuid4().fields[-1])
        try:
            # if point of sale exists, use partner barcode rule
            # but do not require it as a dependence
            rule = self.env.ref("point_of_sale.barcode_rule_client")
            size = 13 - len(rule.pattern)
            ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
            ean = ean[0:12] + str(self.env["barcode.nomenclature"].ean_checksum(ean))
        except ValueError:
            ean = ean[:13]
        return ean

    # todo rename to active
    valid = fields.Boolean(default=True, string="Active")
    barcode = fields.Char("Barcode", oldname="ean13", default=_compute_bar_code)
    partner_id = fields.Many2one("res.partner")
    responsible_id = fields.Many2one(
        "res.users", default=_get_current_user, string="Responsible"
    )
    end_date = fields.Date(readonly=True, string="Expiration Date")
    comment = fields.Char("Reason", required=True)
