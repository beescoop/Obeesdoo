# -*- coding: utf-8 -*-

# Copyright 2018 Rémy Taymans <remytaymans@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'BEES coop Website POS Order',

    'summary': """
    Allow a user to access to his POS Order in the website.
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
        'report',
        'point_of_sale',
    ],

    'data': [
        'views/beesdoo_website_pos_order_templates.xml',
    ]
}
