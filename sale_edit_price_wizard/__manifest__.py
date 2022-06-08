# Copyright 2022 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Edit Price Wizard",
    "summary": """
        Add "Edit Price" submenu on Point Of Sale, Purchase and Sale modules.""",
    "version": "12.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "product",
        "purchase",
        "sale",
        "sale_suggested_price",
        "product_main_supplier",
    ],
    "external_dependencies": {
        "python": ["openupgradelib"],
    },
    "excludes": [],
    "data": [
        "views/product_template_views.xml",
        "views/purchase_views.xml",
        "views/sale_views.xml",
        "wizard/views/adapt_sales_price_wizard_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "pre_init_hook": "rename_xml_ids",
}
