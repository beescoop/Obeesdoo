from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def solidarity_counter(self):
        """
        Calculate the value of the solidarity counter. The initial value is
        stored in parameter 'solidarity_counter_start_value'.
        :return: Integer
        """
        offers = self.env["beesdoo.shift.solidarity.offer"].search([])
        requests = self.env["beesdoo.shift.solidarity.request"].search([])
        start_value = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("shift.solidarity_counter_start_value")
        )
        return start_value + offers.counter() - requests.counter()
