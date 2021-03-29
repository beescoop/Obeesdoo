# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderGenerator(models.Model):
    _description = "Purchase Order Generator"
    _name = "purchase.order.generator"
    _order = "id desc"

    name = fields.Char(string="POG Reference", default="New")
    order_date = fields.Datetime(
        string="Purchase Order Date",
        default=fields.Datetime.now,
        help="Date at which the Quotation should be validated and "
        "converted into a purchase order.",
    )
    date_planned = fields.Datetime(
        string="Date Planned", default=fields.Datetime.now
    )
    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        readonly=True,
        help="Supplier of the purchase order.",
    )
    pog_line_ids = fields.One2many(
        comodel_name="purchase.order.generator.line",
        inverse_name="cpo_id",
        string="Order Lines",
    )
    total_amount = fields.Float(
        string="Total Amount (w/o VAT)", compute="_compute_pog_total"
    )
    generated_purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="original_cpo_id",
        string="Generated Purchase Orders",
    )
    generated_po_count = fields.Integer(
        string="Generated Purchase Order count",
        compute="_compute_generated_po_count",
    )

    @api.multi
    @api.depends("pog_line_ids", "pog_line_ids.purchase_quantity")
    def _compute_pog_total(self):
        for cpo in self:
            total_amount = sum(cpol.subtotal for cpol in cpo.pog_line_ids)
            cpo.total_amount = total_amount

    @api.model
    def _get_selected_supplier(self):
        product_ids = self.env.context.get("active_ids", [])
        products = self.env["product.template"].browse(product_ids)
        suppliers = products.mapped("main_supplier_id")

        if not suppliers:
            raise ValidationError(
                _("No supplier is set for selected articles.")
            )
        elif len(suppliers) == 1:
            return suppliers
        else:
            raise ValidationError(
                _("You must select article from a single supplier.")
            )

    @api.model
    def test_generate_pog(self):
        order_line_obj = self.env["purchase.order.generator.line"]
        product_ids = self.env.context.get("active_ids", [])

        supplier = self._get_selected_supplier()
        name = "POG {} {}".format(supplier.name, fields.Date.today())
        cpo = self.create({"name": name, "supplier_id": supplier.id})

        for product_id in product_ids:
            supplierinfo = self.env["product.supplierinfo"].search(
                [
                    ("product_tmpl_id", "=", product_id),
                    ("name", "=", supplier.id),
                ],
                order="date_start desc",
                limit=1,
            )

            if not supplierinfo:
                product_name = (
                    self.env["product.template"].browse(product_id).name
                )
                raise ValidationError(
                    _("No supplier defined for product %s") % product_name
                )

            min_qty = supplierinfo.min_qty if supplierinfo else 0
            order_line_obj.create(
                {
                    "cpo_id": cpo.id,
                    "product_template_id": product_id,
                    "purchase_quantity": min_qty,
                }
            )
        action = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order.generator",
            "res_id": cpo.id,
            "view_type": "form",
            "view_mode": "form,tree",
            "target": "current",
        }
        return action

    @api.multi
    def create_purchase_order(self):
        self.ensure_one()

        if sum(self.pog_line_ids.mapped("purchase_quantity")) == 0:
            raise ValidationError(
                _(
                    "You need at least a product to generate "
                    "a Purchase Order"
                )
            )

        purchase_order = self.env["purchase.order"].create(
            {
                "date_order": self.order_date,
                "partner_id": self.supplier_id.id,
                "date_planned": self.date_planned,
            }
        )

        for cpo_line in self.pog_line_ids:
            if cpo_line.purchase_quantity > 0:
                product = cpo_line.product_template_id.product_variant_id
                pol = self.env["purchase.order.line"].create(
                    {
                        "name": cpo_line.name,
                        "product_id": product.id,
                        "product_qty": cpo_line.purchase_quantity,
                        "price_unit": cpo_line.product_price,
                        "product_uom": cpo_line.uom_po_id.id,
                        "order_id": purchase_order.id,
                        "date_planned": self.date_planned,
                    }
                )
                pol.compute_taxes_id()

            self.generated_purchase_order_ids += purchase_order

        action = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "res_id": purchase_order.id,
            "view_type": "form",
            "view_mode": "form,tree",
            "target": "current",
        }
        return action

    @api.multi
    @api.depends("generated_purchase_order_ids")
    def _compute_generated_po_count(self):
        for cpo in self:
            cpo.generated_po_count = len(cpo.generated_purchase_order_ids)

    @api.multi
    def get_generated_po_action(self):
        self.ensure_one()
        action = {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "tree,form,kanban",
            "target": "current",
            "domain": [("id", "in", self.generated_purchase_order_ids.ids)],
        }
        return action
