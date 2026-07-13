# SPDX-FileCopyrightText: 2020 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "POS - Can Partner Shop",
    "summary": """Display in the POS whether the partner can shop or not.""",
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "16.0.1.0.2",
    "depends": ["point_of_sale", "shift"],
    "maintainers": ["remytms"],
    "assets": {
        "point_of_sale.assets": [
            "pos_shift_partner_can_shop/static/src/js/ActionpadWidget.esm.js",
            "pos_shift_partner_can_shop/static/src/xml/ActionpadWidget.xml",
            "pos_shift_partner_can_shop/static/src/css/pos_shift_partner_can_shop.css",
        ],
    },
    "installable": True,
    "license": "AGPL-3",
}
