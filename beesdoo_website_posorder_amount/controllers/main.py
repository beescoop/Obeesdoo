# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from itertools import groupby

from odoo.http import request

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
        values["posorder_amount"] = sum(
            po.amount_total for po in owned_posorder
        )
        values["posorder_amount_by_year"] = [
            {
                "year": key,
                "amount": sum(element.amount_total for element in group),
            }
            for key, group in groupby(
                owned_posorder, key=lambda element: element.date_order.year
            )
        ]
        values["company_currency"] = (
            request.env["res.company"]._company_default_get().currency_id
        )
        return values
