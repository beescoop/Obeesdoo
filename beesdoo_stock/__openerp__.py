# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRLfs
# Nicolas Jamoulle, <nicolas@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Action on products in receipt",
    "version": "9.0.1.0",
    "depends": [
        'stock',
    ],
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "website": "www.coopiteasy.be",
    "description": """
        Enable action on multiple lines of a receipt via checkboxes
    """,
    "data": [
        'views/stock_view.xml',
    ],
    'installable': True,
}
