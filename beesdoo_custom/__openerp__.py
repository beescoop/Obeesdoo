# -*- coding: utf-8 -*-
{
    'name': "beesdoo_custom",

    'summary': """
        View and field definition specific to BEES' needs.   
     """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'beesdoo_product',
    ],

    # always loaded
    'data': [
        'views/beesdoo_product.xml',
    ],
}
