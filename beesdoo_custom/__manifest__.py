# Copyright 2017 - 2020 BEES coop SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "BEES coop Custom",

    'description': """
        View and field definition specific to BEES' needs.
     """,

    'author': "Beescoop - Cellule IT, Coop IT Easy",
    'website': "https://github.com/beescoop/Obeesdoo",
    'category': 'Sales Management',
    'version': '12.0.1.0.0',
    'depends': [
        'beesdoo_product',
        'beesdoo_stock_coverage',
        'purchase',
        'easy_my_coop',  # for product views
    ],
    'data': [
        'views/beesdoo_product.xml',
    ],
}
