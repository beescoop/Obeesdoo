from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session",
        default=False,
    )

    @api.constrains('child_eater_ids', 'parent_eater_id')
    def _check_number_of_eaters(self):
        """
        Check the maximum number of eaters that can be assigned to a
        share owner.
        """
        self.ensure_one()
        share_type = None
        if self.cooperator_type:
            share_type = (
                self.env['product.template']
                .search([('default_code', '=', self.cooperator_type)])
            )[0]
        # If the current partner owns no share, check his parent.
        if not share_type:
            share_type = (
                self.env['product.template']
                .search([
                    ('default_code', '=', self.parent_eater_id.cooperator_type)
                ])
            )[0]
        if (
            share_type
            and share_type.max_nb_eater_allowed >= 0
            and len(self.child_eater_ids) > share_type.max_nb_eater_allowed
        ):
            raise ValidationError(
                _('You can only set %d additional eaters per worker')
                % share_type.max_nb_eater_allowed
            )
