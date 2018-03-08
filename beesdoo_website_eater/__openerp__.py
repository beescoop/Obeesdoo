# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'BEES coop Website Eater',

    'summary': """
    Show the eaters of a cooperator in the website portal.
    """,
    'description': """
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.1.0',
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Website',

    'depends': [
        'website',
        'website_portal_v10',
        'beesdoo_base',
    ],

    'data': [
        'views/beesdoo_website_eater_templates.xml',
    ]
}
