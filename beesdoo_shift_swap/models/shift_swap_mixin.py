from odoo import _, models
from odoo.exceptions import MissingError


class ShiftSwapMixin(models.AbstractModel):
    _name = "beesdoo.shift.swap.mixin"
    _description = "beesdoo.shift.swap.mixin"

    def get_validate_date(self):
        self.ensure_one()
        return self.create_date

    def update_shift_data(self, shift, swap_subscription_done):
        """
        Update shift informations with object data
        :param shift: a dict containing data for one shift
        :param swap_subscription_done: beesdoo.shift.swap id list
        :return: dict, beesdoo.shift.swap ids list, Boolean
        """
        raise MissingError(_("Not implemented"))
