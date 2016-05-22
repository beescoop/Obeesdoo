# -*- coding: utf-8 -*-
from openerp import models, fields, api

class RequestLabelPrintingWizard(models.TransientModel):

    _name = 'label.printing.wizard'

    def _get_selected_products(self):
        return self.env.context['active_ids']

    product_ids = fields.Many2many('product.template', default=_get_selected_products)


    @api.one
    def request_printing(self):
        for product in self.product_ids:
            product._request_label_printing()

    @api.one
    def set_as_printed(self):
        for product in self.product_ids:
            product._set_label_as_printed()
