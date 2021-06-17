from odoo import fields, models


class Exchange(models.Model):
    _name = "beesdoo.shift.exchange"

    first_shift = fields.Many2one("beesdoo.shift.shift", string="first_shift")
    second_shift = fields.Many2one(
        "beesdoo.shift.shift", string="second_shift"
    )
    first_request_id = fields.One2many(
        comodel_name="beesdoo.shift.exchange_request",
        inverse_name="exchange_id",
        string="first_request",
    )
    second_request_id = fields.One2many(
        comodel_name="beesdoo.shift.exchange_request",
        inverse_name="exchange_id",
        string="second_request",
    )
    status_generated = fields.Selection(
        [
            ("exchanged_generated", "0"),
            ("first_shift_not_generated", "1"),
            ("second_shift_not_generated", "2"),
            ("both_not_generated", "3"),
        ]
    )
