# -*- coding: utf-8 -*-
{
    'name': "Bees Purchase",

    'summary': """
        Extension du module Purchase""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','beesdoo_product'],

    # always loaded
    'data': [
        'views/purchase_order.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
}