# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from itertools import groupby

from odoo.http import request
from odoo.tools import float_repr

from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalPosOrderAmount(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(
            PortalPosOrderAmount, self
        )._prepare_portal_layout_values()
        user = request.env.user
        owned_posorder = (
            request.env["pos.order"]
            .sudo()
            .search(
                [
                    (
                        "partner_id",
                        "=",
                        user.partner_id.commercial_partner_id.id,
                    ),
                    ("state", "!=", "cancel"),
                ]
            )
        )
        values["posorder_amount"] = float_repr(
            sum(po.amount_total for po in owned_posorder), 2
        )
        values["posorder_amount_by_year"] = [
            {
                "year": year,
                "amount": float_repr(
                    sum(
                        pos_order.amount_total
                        for pos_order in grouped_pos_orders
                    ),
                    2,
                ),
            }
            for year, grouped_pos_orders in groupby(
                owned_posorder, key=lambda pos_order: pos_order.date_order.year
            )
        ]
        values["company_currency"] = (
            request.env["res.company"]._company_default_get().currency_id
        )
        return values
