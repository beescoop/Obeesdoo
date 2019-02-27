# Copyright 2019 Coop IT Easy SCRLfs
# 	    Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Require Product Quantity in POS",
    "version": "9.0.0.1.0",
    "author": "Coop IT Easy SCRLfs",
    "website": "www.coopiteasy.be",
    "license": "AGPL-3",
    "category": "Point of Sale",
    "description": """
        When adding a product to order line, this module sets the quantity to 
          - 1 for "Unit" product,
          - 0 for other product.
        A popup is shown if product quantity is set to 0 when clicking on 
        "Payment" button.  
    """,
    "depends": [
        'point_of_sale',
    ],
    'data': [
        'views/pos_config.xml',
        'static/src/xml/templates.xml',
    ],
    'installable': True,
}
