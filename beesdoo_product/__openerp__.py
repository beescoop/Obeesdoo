# -*- coding: utf-8 -*-
{
    'name': "beesdoo_product",

    'summary': """
        Modification of product module for the needs of beescoop
        - SOOO5 - Ajout de label bio/ethique/provenance""",

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
    'depends': ['beesdoo_base', 'product', 'sale', 'purchase', 'point_of_sale'],

    # always loaded
    'data': [
        'data/product_label.xml',
        'views/beesdoo_product.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
