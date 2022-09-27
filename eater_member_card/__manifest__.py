# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Robin Keunen <robin@coopiteasy.be>
#   - Houssine bakkali <houssine@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Eater Member Card",
    "author": "Beescoop - Cellule IT, Coop IT Easy SC",
    "summary": "Compute barcode based on eaters",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "depends": ["eater", "member_card"],
    "data": [
        "views/partner.xml",
        "report/member_card_template.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
