from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # create_uid must mirror the supervisor_id value.
    # create_uid is a magic field that belongs to the ORM that is not
    # editable via a form.
    create_uid = fields.Many2one(
        comodel_name="res.users", compute="_compute_create_uid"
    )
    supervisor_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
    )
    select_all_purchase_price = fields.Boolean(default=False)
    select_all_selling_price = fields.Boolean(default=False)

    @api.depends("supervisor_id")
    def _compute_create_uid(self):
        for rec in self:
            if rec.supervisor_id:
                rec.create_uid = rec.supervisor_id

    @api.multi
    def write(self, vals):
        if "supervisor_id" in vals:
            new_partner = (
                self.env["res.users"]
                .browse(vals["supervisor_id"])
                .partner_id.id
            )
            for rec in self:
                rec.message_unsubscribe(
                    partner_ids=rec.supervisor_id.partner_id.ids
                )
                rec.message_subscribe(
                    partner_ids=[new_partner], subtype_ids=[]
                )
        return super(PurchaseOrder, self).write(vals)

    @api.multi
    def action_select_deselect_adapt_purchase_price(self):
        self.select_all_purchase_price = not self.select_all_purchase_price
        for order in self:
            for line in order.order_line:
                line.adapt_purchase_price = self.select_all_purchase_price

    @api.multi
    def action_select_deselect_adapt_selling_price(self):
        self.select_all_selling_price = not self.select_all_selling_price
        for order in self:
            for line in order.order_line:
                line.adapt_selling_price = self.select_all_selling_price

    @api.multi
    def button_adapt_price(self):
        for order in self:
            lines = order.order_line.filtered(
                lambda l: l.adapt_purchase_price or l.adapt_selling_price
            )
            for line in lines:
                product_id = line.product_id
                product_tmpl_id = product_id.product_tmpl_id
                seller = product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order
                    and line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                    params={"order_id": line.order_id},
                )
                if seller:
                    price = line.price_unit
                    suggested_price = (
                        price * product_tmpl_id.uom_po_id.factor
                    ) * (1 + product_tmpl_id.categ_id.profit_margin / 100)
                    if line.adapt_purchase_price and line.adapt_selling_price:
                        # will asynchronously trigger _compute_cost()
                        # on `product.template` in `beesdoo_product`
                        seller.price = price
                        product_tmpl_id.list_price = suggested_price
                    elif line.adapt_purchase_price:
                        seller.price = price  # see above comment
                    elif line.adapt_selling_price:
                        product_tmpl_id.list_price = suggested_price
                else:
                    raise UserError(
                        _(
                            "Odoo cannot adapt the price of '%s'.\n"
                            "Please check the Vendor's line on the product page.\n"
                            "Make sure everything is consistent, in particular:\n"
                            "- the purchased quantity might be lower than "
                            "the minimal quantity defined for this vendor\n"
                            "- there might be an issue with the dates "
                            "if there are existing dates on the vendor's line "
                            "for this product."
                        )
                        % product_id.name
                    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    adapt_purchase_price = fields.Boolean(
        default=False,
        string="Adapt vendor purchase price",
        help="Check this box to adapt the purchase price "
        "on the product page when confirming Purchase Order",
    )

    adapt_selling_price = fields.Boolean(
        default=False,
        string="Adapt product seling price",
        help="Check this box to adapt the selling price "
        "on the product page when confirming Purchase Order",
    )
