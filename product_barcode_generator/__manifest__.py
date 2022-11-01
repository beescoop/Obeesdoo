# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Product Barcode Generator",
    "summary": """
        Product Barcode Generator""",
    "version": "12.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "product",
        "pos_price_to_weight",
    ],
    "excludes": [],
    "data": [
        "views/product_template_view.xml",
        "data/product_sequence.xml",
        "data/barcode_rule.xml",
    ],
    "demo": [],
    "qweb": [],
    "pre_init_hook": "rename_beesdoo",
}
