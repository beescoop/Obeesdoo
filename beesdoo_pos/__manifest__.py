# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Elouan Lebars <elouan@coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
#   - Elise Dupont
#   - Thibault François
#   - Grégoire Leeuwerck
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Beescoop Point of sale",

    'summary': """
        Module that extends the pos for the beescoop
    """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Point Of Sale',
    'version': '12.0.1.0.0',

    'depends': ['beesdoo_base', 'beesdoo_product'],

    'data': [
        'security/ir.model.access.csv',
        'views/beesdoo_pos.xml',
        'data/email.xml',
        'data/default_barcode_pattern.xml',
        'data/cron.xml',
    ],
    'qweb': ['static/src/xml/templates.xml'],

    'installable': True,
}
