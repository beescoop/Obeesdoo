# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'BEES coop Website Portal',

    'description': """
    Extension of the Website Portal that prevent modification of sensible data by the users
    """,

    'author': 'Rémy Taymans',
    'license': 'AGPL-3',
    'version': '9.0.1.0',
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',

    'depends': [
        'website',
        'website_portal_extend',
    ],

    'data': [
        'views/portal_website_templates.xml',
    ]
}
