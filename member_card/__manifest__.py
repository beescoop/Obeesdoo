# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Robin Keunen <robin@coopiteasy.be>
#   - Houssine bakkali <houssine@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Member Card",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "summary": "Create a member card and link it to a partner.",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "13.0.1.0.0",
    "depends": ["barcodes"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/member_card_wizards_views.xml",
        "views/partner.xml",
        "views/res_company_view.xml",
        "report/member_card_template.xml",
    ],
    "installable": True,
    "demo": ["demo/cooperators.xml"],
    "license": "AGPL-3",
}
