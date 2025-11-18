# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Beesdoo Deposit Label",
    "summary": "Add the price of the product deposit to the label",
    "version": "16.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["mihien"],
    "license": "AGPL-3",
    "depends": [
        "beesdoo_print_label",
        "pos_container_deposit",
    ],
    "data": [
        "views/report_pricetag_normal.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "/beesdoo_deposit_label/static/scss/pricetag_60x38mm.scss",
        ],
    },
}
