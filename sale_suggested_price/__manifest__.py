# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Suggested Price",
    "summary": """
        Add a suggested price to products, dependent on a product margin in
        partners and product categories.""",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "product_main_supplier",
        "purchase_order_responsible",
        "product",
        "purchase",
        "sale",
    ],
    "excludes": [],
    "data": [
        "views/product_category_views.xml",
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
    ],
    "demo": [],
    "qweb": [],
}
