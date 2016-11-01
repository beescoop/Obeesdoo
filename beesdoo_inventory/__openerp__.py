# -*- coding: utf-8 -*-
{
    'name': "beesdoo_inventory",

    'summary': """
        Modification of inventory data for the needs of beescoop
        - SOO24 - Bon de livraison""",

    'description': """

    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['delivery'],

    # always loaded
    'data': [
        'views/stock.xml'    ],

    # only loaded in demonstration mode
    'demo': [],
}