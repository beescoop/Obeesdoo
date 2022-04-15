# Copyright 2019-2020 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = "res.partner"

    # this field is not displayed in the view
    # cf issue https://github.com/beescoop/Obeesdoo/issues/374
    worker_store = fields.Boolean(
        string="Force Worker",
        help="Check to subscribe member to their shift even"
        " if they are not yet effective cooperator.",
    )
    info_session_confirmed = fields.Boolean(
        string="Confirmed presence to info session", default=False
    )
    is_worker = fields.Boolean(
        compute="_compute_is_worker",
        search="_search_worker",
        readonly=True,
        related="",
    )

    def _cooperator_share_type(self):
        """
        Return the share.type that correspond to the cooperator_type.
        """
        self.ensure_one()
        share_type = self.env["product.template"]
        if self.cooperator_type:
            share_type = (
                self.env["product.template"].search(
                    [("default_code", "=", self.cooperator_type)]
                )
            )[0]
        return share_type

    @api.depends(
        "share_ids",
        "share_ids.share_product_id",
        "share_ids.share_product_id.default_code",
        "share_ids.share_product_id.allow_working",
        "share_ids.share_number",
        "worker_store",
    )
    def _compute_is_worker(self):
        """
        Return True if the partner can participate tho the shift system.
        This is defined on the share type.
        """
        for rec in self:
            share_type = rec._cooperator_share_type()
            if share_type:
                is_worker = share_type.allow_working
            else:
                is_worker = False
            rec.is_worker = is_worker or rec.worker_store

    def _search_worker(self, operator, value):
        lines = self.env["share.line"].search(
            [("share_product_id.allow_working", "=", "True")]
        )
        partner_ids = lines.mapped("partner_id")
        partner_ids |= self.search([("worker_store", "=", True)])
        if (operator, value) in [("=", True), ("!=", False)]:
            return [("id", "in", partner_ids.ids)]
        else:
            return [("id", "not in", partner_ids.ids)]

    @api.depends(
        "cooperative_status_ids",
        "cooperative_status_ids.status",
        "cooperative_status_ids.can_shop",
        "share_ids",
        "share_ids.share_product_id",
        "share_ids.share_product_id.default_code",
        "share_ids.share_number",
    )
    def _compute_can_shop(self):
        """
        Overwrite default behavior to take the owned share into account.
        """
        for rec in self:
            share_type = rec._cooperator_share_type()
            if share_type:
                rec.can_shop = (
                    rec.cooperative_status_ids.can_shop
                    if rec.is_worker and rec.cooperative_status_ids
                    else share_type.allow_shopping
                )
            else:
                rec.can_shop = (
                    rec.cooperative_status_ids.can_shop
                    if rec.is_worker and rec.cooperative_status_ids
                    else False
                )

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
        Check that the parent_eater_id in parnter in self doesn't exceed
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
