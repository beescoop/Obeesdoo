# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    # this field is not displayed in the view
    # cf issue https://github.com/beescoop/Obeesdoo/issues/374
    # force is_worker to True
    worker_store = fields.Boolean(
        string="Force Worker",
        help="Check to subscribe member to their shift even"
        " if they are not yet effective cooperator.",
    )

    is_worker = fields.Boolean(
        compute="_compute_is_worker",
        search="_search_worker",
        readonly=True,
        # override parent definition
        related="",
        help="Computed from the share product of the first cooperator share",
    )

    def _cooperator_share_type(self):
        """
        Return the share.type that correspond to the cooperator_type.
        """
        self.ensure_one()
        share_type = self.env["product.template"]
        # fixme 1 sql request for each partner when executing every _compute_can_*
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
