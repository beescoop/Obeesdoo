# -*- coding: utf-8 -*-
{
    'name': "Beescoop link with easy my coop",

    'summary': """
        Module that made the link between beesdoo customization and easy_my_coop
    """,

    'description': """
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Cooperative management',
    'version': '9.0.1.1.3',

    # any module necessary for this one to work correctly
    'depends': ['beesdoo_base', 'beesdoo_shift', 'easy_my_coop', 'easy_my_coop_eater'],

    # always loaded
    'data': [
        'data/product_share.xml',
        'views/partner.xml',
        'views/res_company.xml',
        'views/subscription_request.xml',
        'views/subscription_templates.xml',
    ],
    'demo': [
        'demo/share_lines.xml',
    ],
    'auto_install': True,
    # only loaded in demonstration mode
}
