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
    "name": "beesdoo_product",
    "summary": """Add scale labels, sale units, and categories.""",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "16.0.1.0.0",
    "depends": [
        "point_of_sale",
        "product",
        "sale",
    ],
    "data": [
        "views/product_template_view.xml",
        "views/scale_category_view.xml",
        "views/uom_category_view.xml",
        "security/ir.model.access.csv",
    ],
    "license": "AGPL-3",
}
