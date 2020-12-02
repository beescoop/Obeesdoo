# Copyright 2020 - BEES coop SCRLfs
#   - Vincent Van Rossem <vincent@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "beesdoo_product_pricelist",
    "summary": """
        Allow quick product price editing
        on point of sale, purchase and sale modules""",
    "author": "Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "depends": ["beesdoo_product", "point_of_sale", "purchase", "sale"],
    "data": [
        "views/product_template_views.xml",
        "views/point_of_sale_view.xml",
        "views/purchase_views.xml",
        "views/sale_views.xml",
        "wizard/adapt_sales_price_wizard_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
