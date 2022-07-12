from odoo import _, models
from odoo.exceptions import MissingError


class ShiftSwapMixin(models.AbstractModel):
    _name = "beesdoo.shift.swap.mixin"
    _description = "beesdoo.shift.swap.mixin"

    def get_validate_date(self):
        self.ensure_one()
        return self.create_date

    def update_shift_data(self, shift, swap_subscription_done):
        raise MissingError(_("Not implemented"))
