from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    cooperator_type = fields.Selection(
        string="Cooperator Type",
        store=True,
        selection="_get_share_type",
        compute="_compute_cooperator_type",
    )
    can_shop = fields.Boolean(
        compute="_compute_can_shop",
        store=True,
    )

    @api.depends(
        "share_ids",
        "share_ids.share_product_id",
        "share_ids.share_product_id.default_code",
        "share_ids.share_number",
    )
    def _compute_cooperator_type(self):
        for partner in self:
            share_type = ""
            for line in partner.share_ids:
                if line.share_number > 0:
                    share_type = line.share_product_id.default_code
                    break
            partner.cooperator_type = share_type

    @api.depends("cooperative_status_ids", "eater", "parent_eater_id")
    def _compute_can_shop(self):
        workers = self.filtered(lambda l: l.eater != "eater" or not l.parent_eater_id)
        eaters = self.filtered(lambda l: l.eater == "eater" and l.parent_eater_id)
        super(Partner, workers)._compute_can_shop()
        for eater in eaters:
            eater.can_shop = eater.parent_eater_id.can_shop
