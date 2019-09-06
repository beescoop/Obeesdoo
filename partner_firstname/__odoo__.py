# -*- coding: utf-8 -*-
{
    'name': "Beescoop Base Module",

    'summary': """
    Module that simply add a firstname on the module res.partner
        replace the community module from the same name for the beescoop
     """,

    'description': """
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Contact',
    'version': '1.0',

    'depends': ['base'],

    'data': [
        'views/res_partner.xml',
    ],
}
