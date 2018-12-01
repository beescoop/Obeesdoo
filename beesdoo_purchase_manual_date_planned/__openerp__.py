# -*- coding: utf-8 -*-
{
    'name': "Bees Purchase Manual date planned",

    'summary': """
        Extension du module Purchase to set manually the date planned for the whole purchase.order""",

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
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/purchase_order.xml',
        'report/report_purchaseorder.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}