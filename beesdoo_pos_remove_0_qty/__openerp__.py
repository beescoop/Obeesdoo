# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: BEES coop (<http://www.bees-coop.be/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Beesdoo - Remove pos order line with quantity set to 0',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'summary': 'Remove pos order line with quantity set to 0',
    'description': """
    This module fix the issue on picking when there is two lines on 
    the pos order for the same product, with one of lines with a 0 quantity.
    The lines at 0 are removed before the pos order is processed to avoid 
    such issue.
    """,
    'author': 'BEES coop - Houssine BAKKALI',
    'website': 'http://www.bees-coop.be',
    'depends': [
        'point_of_sale',
    ],
    'data': [],
    'installable': True,
}
