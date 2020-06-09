# Copyright 2017 - Today Coop IT Easy SCRLfs (<http://www.coopiteasy.be>)
# - Rémy Taymans  <remy@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'BEES coop Website Portal',
    'description': """
    Extension of the Website Portal that prevent modification of sensible data by the users
    """,
    'author': 'Coop IT Easy SCRLfs',
    'license': 'AGPL-3',
    'version': '12.0.1.0.0',
    'website': "https://www.coopiteasy.be",
    'category': 'Cooperative management',
    'depends': [
        'website',
        'website_portal_extend',
    ],
    'data': [
        'views/portal_website_templates.xml',
    ],
    'installable': True,
}
