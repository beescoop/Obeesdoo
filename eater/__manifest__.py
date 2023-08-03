# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Robin Keunen <robin@coopiteasy.be>
#   - Houssine bakkali <houssine@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Eater",
    "summary": "Add eaters to the workers of your structure.",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "15.0.1.0.0",
    "depends": ["base", "partner_firstname"],
    "data": [
        "wizard/new_eater_wizard_views.xml",
        "views/partner.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "demo": ["demo/eaters.xml"],
    "license": "AGPL-3",
}
