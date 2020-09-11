from odoo import api, fields, models


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
    def action_toggle_adapt_purchase_price(self):
        for order in self:
            for line in order.order_line:
                line.adapt_purchase_price ^= True

    @api.multi
    def action_toggle_adapt_selling_price(self):
        for order in self:
            for line in order.order_line:
                line.adapt_selling_price ^= True

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            for line in order.order_line:
                if line.adapt_purchase_price:
                    seller = line.product_id._select_seller(
                        partner_id=line.order_id.partner_id,
                        quantity=line.product_qty,
                        date=order.date_order and order.date_order.date(),
                        uom_id=line.product_uom,
                        params={'order_id': line.order_id}
                    )
                    if seller:
                        seller.price = line.price_unit

        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    adapt_purchase_price = fields.Boolean(
        default=False,
        string='Adapt vendor purchase price',
        help='Check this box to adapt the purchase price on the product page when confirming Purchase Order'
    )

    adapt_selling_price = fields.Boolean(
        default=False,
        string='Adapt product seling price',
        help='Check this box to adapt the selling price on the product page when confirming Purchase Order'
    )


