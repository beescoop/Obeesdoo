# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Houssine BAKKALI <houssine@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "beesdoo_product",
    "summary": """
        Modification of product module for the needs of beescoop
        - SOOO5 - Ajout de label bio/ethique/provenance""",
    "description": """

    """,
    "author": "Beescoop - Cellule IT",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Sales",
    "version": "12.0.1.0.0",
    "depends": [
        "beesdoo_base",
        "product",
        "sale",
        "point_of_sale",
        "pos_price_to_weight",  # OCA
    ],
    "data": [
        "data/product_label.xml",
        "data/barcode_rule.xml",
        "data/product_sequence.xml",
        "views/beesdoo_product.xml",
        "wizard/views/label_printing_utils.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
