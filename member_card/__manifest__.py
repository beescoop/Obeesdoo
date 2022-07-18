# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Robin Keunen <robin@coopiteasy.be>
#   - Houssine bakkali <houssine@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Member Card",
    "author": "Beescoop - Cellule IT, Coop IT Easy SC",
    "summary": "Create a member card and link it to a partner.",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "12.0.1.0.1",
    "depends": ["barcodes", "partner_firstname"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizard/membercard_new_wizard.xml",
        "views/partner.xml",
    ],
    "installable": True,
    "demo": ["demo/cooperators.xml", "demo/eaters.xml"],
    "license": "AGPL-3",
}
