# -*- coding: utf-8 -*-
{
    'name': "Beescoop Base Module",

    'summary': """
		Module that customize the base module and contains some python tools
     """,

    'description': """
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Project Management',
    'version': '0.1',

    'depends': ['point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'wizard/views/new_member_card.xml',
    ],
}
