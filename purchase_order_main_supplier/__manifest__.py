# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Purchase Order Main Supplier",
    "summary": """
        Add a Main Sellers Filter in a Purchase Order.""",
    "version": "12.0.1.0.0",
    "category": "Purchase",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "purchase",
        "product_main_supplier",
    ],
    "excludes": [],
    "data": ["views/purchase_order.xml"],
    "demo": [],
    "qweb": [],
}
