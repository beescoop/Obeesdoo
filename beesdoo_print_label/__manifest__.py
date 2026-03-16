# Copyright 2022 Coop IT Easy SC <http://coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Beesdoo Print Label",
    "summary": """Product labels""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "Coop IT Easy SC, Polln group",
    "website": "https://github.com/beescoop/Obeesdoo",
    "depends": [
        "beesdoo_product_label",
        "product_brand",
        "product_main_supplier",
        "product_print_category",
        "sale_product_deposit",
    ],
    "data": [
        "views/report_pricetag_normal.xml",
        "data/product_print_category.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "/beesdoo_print_label/static/css/pricetag_60x38mm.scss",
        ],
    },
}
