# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Product Label Print Request",
    "summary": "Facilitation for label printing",
    "version": "16.0.1.0.0",
    "category": "Sales/Sales",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": [
        "victor-champonnois",
    ],
    "license": "AGPL-3",
    "depends": [
        "beesdoo_product_label",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "wizard/label_printing_utils.xml",
    ],
}
