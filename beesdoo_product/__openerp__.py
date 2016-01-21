# -*- coding: utf-8 -*-
{
    'name': "beesdoo_product",

    'summary': """
        SOOO5 - Ajout de label bio/ethique/provenance""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views.xml',
        'templates.xml',
        'data/product_label.xml',
        'data/label_color.xml',
        'views/beesdoo_product.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}