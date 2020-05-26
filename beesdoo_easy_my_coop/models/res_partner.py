# Copyright 2019-2020 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session",
        default=False,
    )
    is_worker = fields.Boolean(
        compute="_is_worker",
        search="_search_worker",
        readonly=True,
        related=""
    )

    @api.depends(
        'share_ids',
        'share_ids.share_product_id',
        'share_ids.share_product_id.default_code',
        'share_ids.share_number',
    )
    def _is_worker(self):
        """
        Return True if the partner can participate tho the shift system.
        This is defined on the share type.
        """
        for rec in self:
            share_type = None
            if rec.cooperator_type:
                share_type = (
                    self.env['product.template']
                    .search([('default_code', '=', rec.cooperator_type)])
                )[0]
            if share_type:
                rec.is_worker = share_type.allow_working
                rec.worker_store = share_type.allow_working
            else:
                rec.is_worker = False
                rec.worker_store = False

    def _search_worker(self, operator, value):
        return [('worker_store', operator, value)]

    @api.constrains('child_eater_ids', 'parent_eater_id')
    def _check_number_of_eaters(self):
        """
        Check the maximum number of eaters that can be assigned to a
        share owner.
        """
        for rec in self:
            share_type = None
            if rec.cooperator_type:
                share_type = (
                    self.env['product.template']
                    .search([('default_code', '=', rec.cooperator_type)])
                )[0]
            # If the current partner owns no share, check his parent.
            if not share_type:
                share_type = (
                    self.env['product.template']
                    .search([
                        (
                            'default_code',
                            '=',
                            rec.parent_eater_id.cooperator_type
                        )
                    ])
                )[0]
            if (
                share_type
                and share_type.max_nb_eater_allowed >= 0
                and len(rec.child_eater_ids) > share_type.max_nb_eater_allowed
            ):
                raise ValidationError(
                    _('You can only set %d additional eaters per worker')
                    % share_type.max_nb_eater_allowed
                )
