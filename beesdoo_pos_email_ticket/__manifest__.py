# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Vincent Van Rossem <vincent@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
#   - Grégoire Leeuwerck
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "BEES coop Send POS ticket by email",
    "summary": """This module adds the eaters of the customer to the POS
    ActionpadWidget and PaymentScreenWidget.""",
    "author": "BEES coop - Cellule IT, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Point Of Sale",
    "version": "12.0.1.1.0",
    "depends": ["point_of_sale"],
    "data": ["views/beesdoo_pos.xml", "data/cron.xml", "data/email.xml"],
    "qweb": ["static/src/xml/templates.xml"],
    "installable": True,
    "license": "AGPL-3",
    "development_status": "Beta",
}
