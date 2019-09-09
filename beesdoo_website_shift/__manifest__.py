
# Copyright 2017-2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'BEES coop Website Shift',

    'summary': """
        Show available shifts for regular and irregular workers on the
        website and let workers manage their shifts with an
        easy web interface.
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.2.3.1',
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',

    'depends': ['website', 'beesdoo_shift'],

    'data': [
        'data/res_config_data.xml',
        'views/shift_website_templates.xml',
        'views/my_shift_website_templates.xml',
        'views/res_config_views.xml',
    ]
}
