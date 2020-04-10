from odoo import models, fields, api

class RequestLabelPrintingWizard(models.TransientModel):
    _name = 'label.printing.wizard'
    _description = 'label.printing.wizard'

    def _get_selected_products(self):
        return self.env.context['active_ids']

    product_ids = fields.Many2many('product.template', default=_get_selected_products)


    @api.one
    def request_printing(self):
        self.product_ids.write({'label_to_be_printed' : True})


    @api.one
    def set_as_printed(self):
        self.product_ids.write({'label_to_be_printed' : False, 'label_last_printed' : fields.Datetime.now()})
