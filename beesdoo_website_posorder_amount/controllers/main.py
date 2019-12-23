# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.addons.website_portal_v10.controllers.main import WebsiteAccount
from openerp.http import request


class PortalPosOrderAmount(WebsiteAccount):

    def _prepare_portal_layout_values(self):
        values = super(
            PortalPosOrderAmount, self
        )._prepare_portal_layout_values()
        user = request.env.user
        owned_posorder = request.env["pos.order"].sudo().search(
            [
                ("partner_id", "=", user.partner_id.commercial_partner_id.id),
                ("state", "!=", "cancel"),
            ]
        )
        values["posorder_amount"] = sum(
            po.amount_total for po in owned_posorder
        )
        values["company_currency"] = (
            request.env["res.company"]._company_default_get().currency_id
        )
        return values
