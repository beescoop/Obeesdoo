# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "sale_suggested_price",
    "summary": """
        Add a suggested price to products, dependent on a product margin in
        partners and product categories.""",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://coopiteasy.be",
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "account",
        "product",
        "purchase",
        "sale",
    ],
    "excludes": [],
    "data": [
        "views/product_category_views.xml",
        "views/product_supplierinfo_views.xml",
        "views/product_template_views.xml",
        "views/purchase_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
        "views/sale_views.xml",
        "wizard/views/adapt_sales_price_wizard_view.xml",
    ],
    "demo": [],
    "qweb": [],
}
