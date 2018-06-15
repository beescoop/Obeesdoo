# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import ValidationError


class ComputedPurchaseOrder(models.Model):
    _description = 'Computed Purchase Order'
    _name = 'computed.purchase.order'
    _order = 'id desc'

    name = fields.Char(
        string='CPO Reference',
        size=64,
        default='New')

    order_date = fields.Datetime(
        string='Purchase Order Date',
        default=fields.Datetime.now,
        help="Depicts the date where the Quotation should be validated and converted into a purchase order.")  # noqa

    date_planned = fields.Datetime(
        string='Date Planned'
    )

    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        readonly=True,
        help="Supplier of the purchase order.")

    order_line_ids = fields.One2many(
        'computed.purchase.order.line',
        'computed_purchase_order_id',
        string='Order Lines',
    )

    total_amount = fields.Float(
        string='Total Amount (w/o VAT)',
        compute='_compute_cpo_total'
    )

    generated_purchase_order_ids = fields.One2many(
        'purchase.order',
        'original_cpo_id',
        string='Generated Purchase Orders',
    )

    generated_po_count = fields.Integer(
        string='Generated Purchase Order count',
        compute='_compute_generated_po_count',
    )

    @api.model
    def default_get(self, fields_list):
        record = super(ComputedPurchaseOrder, self).default_get(fields_list)

        record['date_planned'] = self._get_default_date_planned()
        record['supplier_id'] = self._get_selected_supplier_id()
        record['order_line_ids'] = self._create_order_lines()
        record['name'] = self._compute_default_name()

        return record

    def _get_default_date_planned(self):
        return fields.Datetime.now()

    def _get_selected_supplier_id(self):
        """
        Calcule le vendeur associé qui a la date de début la plus récente et
        plus petite qu’aujourd’hui pour chaque article sélectionné.
        Will raise an error if more than two sellers are set
        """
        if 'active_ids' not in self.env.context:
            return False

        product_ids = self.env.context['active_ids']
        products = self.env['product.template'].browse(product_ids)

        suppliers = set()
        for product in products:
            main_supplier_id = product.main_supplier_id.id
            suppliers.add(main_supplier_id)

        if len(suppliers) == 0:
            raise ValidationError(u'No supplier is set for selected articles.')
        elif len(suppliers) == 1:
            return suppliers.pop()
        else:
            raise ValidationError(
                u'You must select article from a single supplier.')

    def _create_order_lines(self):
        product_tmpl_ids = self._get_selected_products()
        cpol_ids = []
        OrderLine = self.env['computed.purchase.order.line']
        for product_id in product_tmpl_ids:
            cpol = OrderLine.create(
                {'computed_purchase_order_id': self.id,
                 'product_template_id': product_id,
                 }
            )
            # should ideally be set in cpol defaults
            cpol.purchase_quantity = cpol.minimum_purchase_qty
            cpol_ids.append(cpol.id)
        return cpol_ids

    def _compute_default_name(self):
        supplier_id = self._get_selected_supplier_id()
        if supplier_id:
            supplier_name = (
                self.env['res.partner']
                    .browse(supplier_id)
                    .name)

            name = u'CPO {} {}'.format(
                supplier_name,
                fields.Date.today())
        else:
            name = 'New'
        return name

    def _get_selected_products(self):
        if 'active_ids' in self.env.context:
            return self.env.context['active_ids']
        else:
            return []

    @api.multi
    def _compute_generated_po_count(self):
        for cpo in self:
            cpo.generated_po_count = len(cpo.generated_purchase_order_ids)

    @api.multi
    def get_generated_po_action(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form,kanban',
            'target': 'current',
            'domain': [('id', 'in', self.generated_purchase_order_ids.ids)],
        }
        return action

    # @api.onchange(order_line_ids)  # fixme
    @api.multi
    def _compute_cpo_total(self):
        for cpo in self:
            total_amount = sum(cpol.subtotal for cpol in cpo.order_line_ids)
            cpo.total_amount = total_amount

    @api.multi
    def create_purchase_order(self):
        self.ensure_one()

        if sum(self.order_line_ids.mapped('purchase_quantity')) == 0:
            raise ValidationError(u'You need at least a product to generate '
                                  u'a Purchase Order')

        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']

        po_values = {
            'name': 'New',
            'date_order': self.order_date,
            'partner_id': self.supplier_id.id,
            'date_planned': self.date_planned,
        }
        purchase_order = PurchaseOrder.create(po_values)

        for cpo_line in self.order_line_ids:
            if cpo_line.purchase_quantity > 0:
                if cpo_line.supplierinfo_id.product_code:
                    pol_name = '[%s] %s' % (cpo_line.supplierinfo_id.product_code, cpo_line.name)
                else:
                    pol_name = cpo_line.name
                pol_values = {
                    'name': pol_name,
                    'product_id': cpo_line.get_default_product_product().id,
                    'product_qty': cpo_line.purchase_quantity,
                    'price_unit': cpo_line.product_price,
                    'product_uom': cpo_line.uom_po_id.id,
                    'order_id': purchase_order.id,
                    'date_planned': self.date_planned,
                }
                PurchaseOrderLine.create(pol_values)

            self.generated_purchase_order_ids += purchase_order

        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
        return action
