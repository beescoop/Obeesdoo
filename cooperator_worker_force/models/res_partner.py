# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"
    worker_store = fields.Boolean(
        string="Force Worker",
        help="Tick this box to set this partner as worker"
        " even if they are not an effective cooperator.",
    )

    @api.depends(
        "share_ids",
        "share_ids.share_product_id",
        "share_ids.share_product_id.default_code",
        "share_ids.share_product_id.allow_working",
        "share_ids.share_number",
        "worker_store",
    )
    def _compute_is_worker(self):
        super()._compute_is_worker()
        for partner in self:
            partner.is_worker = partner.is_worker or partner.worker_store

    def _search_worker(self, operator, value):
        domain = super()._search_worker(operator, value)
        forced_workers = self.search([("worker_store", "=", True)])
        if (operator, value) in [("=", True), ("!=", False)]:
            forced_worker_domain = [("id", "in", forced_workers.ids)]
        else:
            forced_worker_domain = [("id", "not in", forced_workers.ids)]
        return ["|"] + domain + forced_worker_domain
