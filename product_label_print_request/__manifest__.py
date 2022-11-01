# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Product Label Print Request",
    "summary": """
        Facilitation for label printing.""",
    "version": "12.0.1.0.0",
    "category": "Product",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": ["beesdoo_product_label"],
    "excludes": [],
    "data": [
        "views/product_template_views.xml",
        "wizard/views/label_printing_utils.xml",
    ],
    "demo": [],
    "qweb": [],
    "pre_init_hook": "rename_beesdoo",
}
