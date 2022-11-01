# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Houssine BAKKALI <houssine@coopiteasy.be>
#   - Manuel Claeys Bouuaert <manuel@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Product Hazard",
    "summary": """
        Add hazard and FDS labels to products
        """,
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "depends": [
        "product",
        "sale",
    ],
    "data": [
        "data/product_hazard.xml",
        "views/product_template_view.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "pre_init_hook": "rename_beesdoo",
    "license": "AGPL-3",
}
