# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
#   Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Order Generator",
    "version": "12.0.1.0.0",
    "category": "Purchase Order",
    "summary": "Generate purchase order from a product selection",
    "author": "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/obeesdoo/",
    "license": "AGPL-3",
    "depends": ["purchase", "beesdoo_stock_coverage"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_generator.xml",
        "views/purchase_order.xml",
        "views/product_template.xml",
    ],
}
