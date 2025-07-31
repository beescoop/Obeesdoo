# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
#   - Grégoire Leeuwerck
#   - Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "POS Eater",
    "summary": """This module adds the eaters of the customer to the POS
    ActionpadWidget.""",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "16.0.1.0.0",
    "depends": ["point_of_sale", "eater"],
    "assets": {
        "point_of_sale.assets": [
            "pos_eater/static/src/css/pos.css",
            "pos_eater/static/src/js/**/*.js",
            "pos_eater/static/src/xml/**/*.xml",
        ],
    },
    "installable": True,
    "license": "AGPL-3",
}
