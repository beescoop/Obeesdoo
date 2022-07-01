# Copyright 2019-2020 Coop IT Easy SC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    def _check_number_of_eaters(self):
        """
        This function has been splitted into two functions:
            - _check_max_parent_eaters()
            - _check_max_child_eaters()
        The purpose of this function is to overwrite the function
        defined in beesdoo_base/models/partner.py.
        """

    @api.constrains("parent_eater_id")
    def _check_max_parent_eaters(self):
        """
        Check that the parent_eater_id in partner in self doesn't exceed
        the maximum eater limit.
        See also: _check_max_child_eaters()
        """
        for rec in self:
            if rec.parent_eater_id:
                share_type = rec.parent_eater_id._cooperator_share_type()
                if (
                    share_type
                    and share_type.max_nb_eater_allowed >= 0
                    and len(rec.parent_eater_id.child_eater_ids)
                    > share_type.max_nb_eater_allowed
                ):
                    raise ValidationError(
                        _("You can only set %d additional eaters per worker")
                        % share_type.max_nb_eater_allowed
                    )

    @api.constrains("child_eater_ids")
    def _check_max_child_eaters(self):
        """
        Check the maximum number of eaters that can be assigned to a
        share owner.
        See also: _check_max_parent_eaters()
        """
        for rec in self:
            share_type = rec._cooperator_share_type()
            if (
                share_type
                and share_type.max_nb_eater_allowed >= 0
                and len(rec.child_eater_ids) > share_type.max_nb_eater_allowed
            ):
                raise ValidationError(
                    _("You can only set %d additional eaters per worker")
                    % share_type.max_nb_eater_allowed
                )
