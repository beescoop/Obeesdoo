# -*- coding: utf-8 -*-
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

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Point Of Sale',
    'version': '9.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['beesdoo_base', 'beesdoo_product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/beesdoo_pos.xml',
        'data/email.xml',
        'data/cron.xml',
    ],
    'qweb': ['static/src/xml/templates.xml'],
    # only loaded in demonstration mode
}

