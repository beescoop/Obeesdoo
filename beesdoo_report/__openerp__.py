# -*- coding: utf-8 -*-
{
    'name': "Beescoop Report Module",

    'summary': """
        Module that generate report for Beescoop
    """,

    'description': """
        Beescoop Report
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '0.1',

    'depends': ['beesdoo_base', 'beesdoo_pos', 'board'],

    'data': [
        #YOU PUT YOUR XML HERE
        'report/views/visits.xml', #Should remain the first one
        
        
        'report/views/board.xml', #Should be after the sql view's views
    ],
}

