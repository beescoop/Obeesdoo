# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
#   - Grégoire Leeuwerck
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Beescoop Point of sale",
    "summary": """This module adds the eaters of the customer to the POS
    ActionpadWidget and PaymentScreenWidget.""",
    "author": "Beescoop - Cellule IT, Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "12.0.1.0.0",
    "depends": ["beesdoo_base", "beesdoo_product"],
    "data": ["views/beesdoo_pos.xml", "data/default_barcode_pattern.xml"],
    "qweb": ["static/src/xml/templates.xml"],
    "installable": True,
    "license": "AGPL-3",
}
