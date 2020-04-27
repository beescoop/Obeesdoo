# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Computed Purchase Order",
    "version": "12.0.1.0.0",
    "category": "Purchase Order",
    "summary": "Compute purchase order from selected products",
    "author": "Coop IT Easy",
    "website": "https://github.com/coopiteasy/procurement-addons",
    "license": "AGPL-3",
    "depends": [
        "product",
        "purchase",
        "stock",
        "beesdoo_stock_coverage",
    ],  # todo simplify
    "data": [
        "security/ir.model.access.csv",
        "views/computed_purchase_order.xml",
        "views/purchase_order.xml",
    ],
}
