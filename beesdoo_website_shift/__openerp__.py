# -*- coding: utf-8 -*-
{
    'name': 'Beescoop Shift Website',

    'summary': """
        Show available shifts for regular and irregular workers in
        portal.
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',
    'version': '0.1',

    'depends': ['website', 'beesdoo_shift'],

    'data': [
        'data/res_config_data.xml',
        'views/shift_website_templates.xml',
        'views/res_config_views.xml',
    ]
}
