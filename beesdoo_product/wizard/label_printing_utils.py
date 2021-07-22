from odoo import api, fields, models


# todo move printing functions to specific module
class RequestLabelPrintingWizard(models.TransientModel):
    _name = "label.printing.wizard"
    _description = "label.printing.wizard"

    def _get_selected_products(self):
        return self.env.context["active_ids"]

    product_ids = fields.Many2many(
        "product.template", default=_get_selected_products
    )

    @api.multi
    def request_printing(self):
        self.ensure_one()
        self.product_ids.write({"label_to_be_printed": True})

    @api.multi
    def set_as_printed(self):
        self.ensure_one()
        self.product_ids.write(
            {
                "label_to_be_printed": False,
                "label_last_printed": fields.Datetime.now(),
            }
        )
