# Copyright 2020 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import uuid

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class BeesdooProductHazard(models.Model):
    _name = "beesdoo.product.hazard"
    _description = "beesdoo.product.hazard"

    name = fields.Char()
    type = fields.Selection([("fds", "FDS"), ("hazard", "Specific hazard")])
    active = fields.Boolean(default=True)


class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "eco")]
    )
    local_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "local")]
    )
    fair_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "fair")]
    )
    origin_label = fields.Many2one(
        "beesdoo.product.label", domain=[("type", "=", "delivery")]
    )

    fds_label = fields.Many2one(
        "beesdoo.product.hazard",
        string="FDS label",
        domain=[("type", "=", "fds")],
        translate=True,
    )
    hazard_label = fields.Many2one(
        "beesdoo.product.hazard",
        string="Hazard label",
        domain=[("type", "=", "hazard")],
        translate=True,
    )

    main_seller_id = fields.Many2one(
        "res.partner",
        string="Main Seller",
        compute="_compute_main_seller_id",
        store=True,
    )

    display_unit = fields.Many2one("uom.uom")
    default_reference_unit = fields.Many2one("uom.uom")
    display_weight = fields.Float(
        compute="_compute_display_weight", store=True
    )

    total_with_vat = fields.Float(
        compute="_compute_total",
        store=True,
        string="Total Sales Price with VAT",
    )
    total_with_vat_by_unit = fields.Float(
        compute="_compute_total",
        store=True,
        string="Total Sales Price with VAT by Reference Unit",
    )
    total_deposit = fields.Float(
        compute="_compute_total", store=True, string="Deposit Price"
    )

    label_to_be_printed = fields.Boolean("Print label?")
    label_last_printed = fields.Datetime("Label last printed on")

    note = fields.Text("Comments", copy=False)

    deadline_for_sale = fields.Integer(string="Deadline for sale(days)")
    deadline_for_consumption = fields.Integer(
        string="Deadline for consumption(days)"
    )
    ingredients = fields.Char(string="Ingredient")
    scale_label_info_1 = fields.Char(string="Scale lable info 1")
    scale_label_info_2 = fields.Char(string="Scale lable info 2")
    scale_sale_unit = fields.Char(
        compute="_compute_scale_sale_uom", string="Scale sale unit", store=True
    )
    scale_category = fields.Many2one(
        "beesdoo.scale.category", string="Scale Category"
    )
    scale_category_code = fields.Integer(
        related="scale_category.code",
        string="Scale category code",
        readonly=True,
        store=True,
    )

    @api.depends("uom_id", "uom_id.category_id", "uom_id.category_id.type")
    @api.multi
    def _compute_scale_sale_uom(self):
        for product in self:
            if product.uom_id.category_id.type == "unit":
                product.scale_sale_unit = "F"
            elif product.uom_id.category_id.type == "weight":
                product.scale_sale_unit = "P"

    @api.multi
    def generate_barcode(self):
        self.ensure_one()
        if self.to_weight:
            seq_internal_code = self.env.ref(
                "beesdoo_product.seq_ean_product_internal_ref"
            )
            bc = ""
            if not self.default_code:
                rule = self.env["barcode.rule"].search(
                    [
                        (
                            "name",
                            "=",
                            "Price Barcodes (Computed Weight) 2 Decimals",
                        )
                    ]
                )[0]
                default_code = seq_internal_code.next_by_id()
                while (
                    self.search_count([("default_code", "=", default_code)])
                    > 1
                ):
                    default_code = seq_internal_code.next_by_id()
                self.default_code = default_code
            ean = "02" + self.default_code[0:5] + "000000"
            bc = ean[0:12] + str(
                self.env["barcode.nomenclature"].ean_checksum(ean)
            )
        else:
            rule = self.env["barcode.rule"].search(
                [("name", "=", "Beescoop Product Barcodes")]
            )[0]
            size = 13 - len(rule.pattern)
            ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
            bc = ean[0:12] + str(
                self.env["barcode.nomenclature"].ean_checksum(ean)
            )
            # Make sure there is no other active member with the same barcode
            while self.search_count([("barcode", "=", bc)]) > 1:
                ean = rule.pattern + str(uuid.uuid4().fields[-1])[:size]
                bc = ean[0:12] + str(
                    self.env["barcode.nomenclature"].ean_checksum(ean)
                )
        _logger.info("barcode :", bc)
        self.barcode = bc

    @api.multi
    @api.depends("seller_ids", "seller_ids.date_start")
    def _compute_main_seller_id(self):
        for product in self:
            # todo english code Calcule le vendeur associé qui a la date de
            #  début la plus récente et plus petite qu’aujourd’hui fixme
            #   could product.main_seller_id be used instead? it seems that
            #   “seller” and “supplier” are used interchangeably in this
            #   class. is this on purpose?
            sellers_ids = product._get_main_supplier_info()
            product.main_seller_id = (
                sellers_ids and sellers_ids[0].name or False
            )

    @api.multi
    @api.depends(
        "taxes_id",
        "list_price",
        "taxes_id.amount",
        "taxes_id.tax_group_id",
        "display_weight",
        "weight",
    )
    def _compute_total(self):
        for product in self:
            consignes_group = self.env.ref(
                "beesdoo_product.consignes_group_tax", raise_if_not_found=False
            )

            taxes_included = set(product.taxes_id.mapped("price_include"))
            if len(taxes_included) == 0:
                product.total_with_vat = product.list_price
                return True

            elif len(taxes_included) > 1:
                raise ValidationError(
                    _("Several tax strategies (price_include) defined for %s")
                    % product.name
                )

            elif taxes_included.pop():
                product.total_with_vat = product.list_price
                product.total_deposit = sum(
                    [
                        tax._compute_amount(
                            product.list_price, product.list_price
                        )
                        for tax in product.taxes_id
                        if tax.tax_group_id == consignes_group
                    ]
                )
            else:
                tax_amount_sum = sum(
                    [
                        tax._compute_amount(
                            product.list_price, product.list_price
                        )
                        for tax in product.taxes_id
                        if tax.tax_group_id != consignes_group
                    ]
                )
                product.total_with_vat = product.list_price + tax_amount_sum

            product.total_deposit = sum(
                [
                    tax._compute_amount(product.list_price, product.list_price)
                    for tax in product.taxes_id
                    if tax.tax_group_id == consignes_group
                ]
            )

            if product.display_weight > 0:
                product.total_with_vat_by_unit = (
                    product.total_with_vat / product.weight
                )

    @api.multi
    @api.depends("weight", "display_unit")
    def _compute_display_weight(self):
        for product in self:
            product.display_weight = (
                product.weight * product.display_unit.factor
            )

    @api.multi
    @api.constrains("display_unit", "default_reference_unit")
    def _unit_same_category(self):
        for product in self:
            if (
                product.display_unit.category_id
                != product.default_reference_unit.category_id
            ):
                raise UserError(
                    _(
                        "Reference Unit and Display Unit should belong to the "
                        "same category "
                    )
                )

    @api.multi
    def create_request_label_printing_wizard(self):
        context = {"active_ids": self.ids}
        self.env["label.printing.wizard"].with_context(context).create({})
        print_request_view = self.env.ref(
            "beesdoo_product.printing_label_request_wizard"
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "label.printing.wizard",
            "view_type": "form",
            "view_mode": "form",
            "print_request_view": print_request_view.id,
            "target": "new",
        }


class BeesdooScaleCategory(models.Model):
    _name = "beesdoo.scale.category"
    _description = "beesdoo.scale.category"

    name = fields.Char(string="Scale name category")
    code = fields.Integer(string="Category code")

    _sql_constraints = [
        (
            "code_scale_categ_uniq",
            "unique (code)",
            "The code of the scale category must be unique !",
        )
    ]


class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"
    _description = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection(
        [
            ("eco", "Écologique"),
            ("local", "Local"),
            ("fair", "Équitable"),
            ("delivery", "Distribution"),
        ]
    )
    color_code = fields.Char()
    active = fields.Boolean(default=True)


class BeesdooProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    price = fields.Float("Price")


class BeesdooUOMCateg(models.Model):
    _inherit = "uom.category"

    type = fields.Selection(
        [
            ("unit", "Unit"),
            ("weight", "Weight"),
            ("time", "Time"),
            ("distance", "Distance"),
            ("surface", "Surface"),
            ("volume", "Volume"),
            ("other", "Other"),
        ],
        string="Category type",
        default="unit",
    )
