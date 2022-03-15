# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import SUPERUSER_ID, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    original_cpo_id = fields.Many2one(
        "purchase.order.generator",
        string="Original POG",
        help="POG used to generate this Purchase Order",
    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def compute_taxes_id(self):
        for pol in self:
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
            else:
                company_id = self.company_id.id

            fpos_id = (
                self.env["account.fiscal.position"]
                .with_context(company_id=company_id)
                .get_fiscal_position(pol.partner_id.id)
            )
            fpos = self.env["account.fiscal.position"].browse(fpos_id)
            pol.order_id.fiscal_position_id = fpos

            taxes = self.product_id.supplier_taxes_id
            taxes_id = fpos.map_tax(taxes) if fpos else taxes

            if taxes_id:
                taxes_id = taxes_id.filtered(lambda t: t.company_id.id == company_id)

            pol.taxes_id = taxes_id
