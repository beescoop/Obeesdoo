from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def solidarity_counter(self):
        offers = self.env["beesdoo.shift.solidarity.offer"].search([])
        requests = self.env["beesdoo.shift.solidarity.request"].search([])
        start_value = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("beesdoo_shift.solidarity_counter_start_value")
        )
        return start_value + offers.counter() + requests.counter()
