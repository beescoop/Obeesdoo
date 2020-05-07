# Copyright 2017 - 2020 BEES coop SCRLfs
#   - Augustin Borsu
#   - Elise Dupont
#   - Thibault François
#   - Jean-Marc François
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Beesdoo Inventory",

    'summary': """
        Adds a responsible, a max shipping date and a button to copy quantity to
        stock pickings.""",

    'description': """

    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",
    'category': 'Inventory',
    'version': '12.0.1.0.0',
    'depends': ['delivery', 'beesdoo_base', 'beesdoo_product'],
    'data': [
        'views/stock.xml'
    ],
    'installable': True,
}
