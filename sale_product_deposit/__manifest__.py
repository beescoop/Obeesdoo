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
    "name": "Sale Product Deposit Price",
    "summary": """Calculates total price with VAT and deposit price.""",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "16.0.1.0.0",
    "depends": [
        "pos_container_deposit",
        "product",
        "sale",
    ],
    "data": [
        "views/product_template_view.xml",
    ],
    "license": "AGPL-3",
}
