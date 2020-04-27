# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class ComputedPurchaseOrderLine(models.Model):
    _description = "Computed Purchase Order Line"
    _name = "computed.purchase.order.line"

    name = fields.Char(string="Product Name", compute="_compute_name")
    cpo_id = fields.Many2one(
        comodel_name="computed.purchase.order",
        string="Computed Purchase Order",
    )
    product_template_id = fields.Many2one(
        comodel_name="product.template",
        string="Linked Product Template",
        required=True,
        help="Product",
    )
    purchase_quantity = fields.Float(string="Purchase Quantity", default=0.0)
    category_id = fields.Many2one(
        comodel_name="product.category",
        string="Internal Category",
        related="product_template_id.categ_id",
        read_only=True,
    )
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        read_only=True,
        related="product_template_id.uom_id",
        help="Default Unit of Measure used for all stock operation.",
    )
    qty_available = fields.Float(
        string="Stock Quantity",
        related="product_template_id.qty_available",
        read_only=True,
        help="Quantity currently in stock. Does not take "
        "into account incoming orders.",
    )
    virtual_available = fields.Float(
        string="Forecast Quantity",
        related="product_template_id.virtual_available",
        read_only=True,
        help="Virtual quantity taking into account current stock, incoming "
        "orders and outgoing sales.",
    )
    daily_sales = fields.Float(
        string="Average Consumption",
        related="product_template_id.daily_sales",
        read_only=True,
    )
    stock_coverage = fields.Float(
        string="Stock Coverage",
        related="product_template_id.stock_coverage",
        read_only=True,
    )
    uom_po_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Purchase Unit of Measure",
        read_only=True,
        related="product_template_id.uom_po_id",
        help="Default Unit of Measure used for all stock operation.",
    )
    supplierinfo_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Supplier information",
        compute="_compute_supplierinfo",
        store=True,
        readonly=True,
    )
    minimum_purchase_qty = fields.Float(
        string="Minimum Purchase Quantity", related="supplierinfo_id.min_qty"
    )
    product_price = fields.Float(
        string="Product Price (w/o VAT)",
        related="supplierinfo_id.price",
        help="Supplier Product Price by buying unit. Price is  without VAT",
    )
    virtual_coverage = fields.Float(
        string="Expected Stock Coverage",
        compute="_compute_coverage_and_subtotal",
        help="Expected stock coverage (in days) based on current stocks and "
        "average daily consumption",
    )
    subtotal = fields.Float(
        string="Subtotal (w/o VAT)", compute="_compute_coverage_and_subtotal"
    )

    @api.multi
    @api.depends("supplierinfo_id")
    def _compute_name(self):
        for cpol in self:
            if cpol.supplierinfo_id and cpol.supplierinfo_id.product_code:
                product_code = cpol.supplierinfo_id.product_code
                product_name = cpol.product_template_id.name
                cpol_name = "[%s] %s" % (product_code, product_name)
            else:
                cpol_name = cpol.product_template_id.name
            cpol.name = cpol_name

    @api.multi
    @api.onchange("product_template_id")
    def _onchange_purchase_quantity(self):
        for cpol in self:
            cpol.purchase_quantity = cpol.minimum_purchase_qty

    @api.multi
    @api.depends("purchase_quantity")
    def _compute_coverage_and_subtotal(self):
        for cpol in self:
            cpol.subtotal = cpol.product_price * cpol.purchase_quantity
            avg = cpol.daily_sales
            if avg > 0:
                qty = (cpol.virtual_available / cpol.uom_id.factor) + (
                    cpol.purchase_quantity / cpol.uom_po_id.factor
                )
                cpol.virtual_coverage = qty / avg
            else:
                # todo what would be a good default value? (not float(inf))
                cpol.virtual_coverage = 9999

        return True

    @api.multi
    @api.depends("product_template_id")
    def _compute_supplierinfo(self):
        for cpol in self:
            if not cpol.product_template_id:
                continue

            si = self.env["product.supplierinfo"].search(
                [
                    ("product_tmpl_id", "=", cpol.product_template_id.id),
                    ("name", "=", cpol.cpo_id.supplier_id.id),
                ]
            )

            if len(si) == 0:
                raise ValidationError(
                    _("CPO supplier does not sell product {name}").format(
                        name=cpol.product_template_id.name
                    )
                )
            elif len(si) > 1:
                _logger.warning(
                    "product {name} has several supplier info set, chose last".format(
                        name=cpol.product_template_id.name
                    )
                )
            si = si.sorted(key=lambda r: r.create_date, reverse=True)
            cpol.supplierinfo_id = si[0]

    @api.constrains("purchase_quantity")
    def _check_minimum_purchase_quantity(self):
        for cpol in self:
            if cpol.purchase_quantity < 0:
                raise ValidationError(
                    _(
                        "Purchase quantity for {product_name} "
                        "must be greater than 0"
                    ).format(product_name=cpol.product_template_id.name)
                )
            elif 0 < cpol.purchase_quantity < cpol.minimum_purchase_qty:
                raise ValidationError(
                    _(
                        "Purchase quantity for {product_name} "
                        "must be greater than {min_qty}"
                    ).format(
                        product_name=cpol.product_template_id.name,
                        min_qty=cpol.minimum_purchase_qty,
                    )
                )
