# Copyright 2022 Coop IT Easy SC <http://coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Beesdoo Print Label",
    "summary": """Product labels""",
    "version": "12.0.2.0.0",
    "license": "AGPL-3",
    "category": "Sales",
    "author": "Coop IT Easy SC, Polln group",
    "website": "https://github.com/beescoop/Obeesdoo",
    "depends": [
        "beesdoo_product",
        "product_print_category",
        "product_brand",
    ],
    "data": [
        "views/report_pricetag_normal.xml",
        "data/product_print_category.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
