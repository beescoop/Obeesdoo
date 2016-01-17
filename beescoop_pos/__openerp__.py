# -*- coding: utf-8 -*-
{
    'name': "bees_member",

    'summary': """
        	Module to manage bees members
	""",

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
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'beescoop_pos.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}