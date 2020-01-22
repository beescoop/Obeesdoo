# -*- coding: utf-8 -*-
{
    'name': "Beescoop Purchase - Manual date planned",

    'summary': """
        Extension of module Purchase to manually set the planned date for the whole purchase.order
    """,

    'description': """

    """,

    'author': "Beescoop - Cellule IT, Elouan Le Bars",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Purchase',
    'version': '9.0.1.0.1',

    'depends': ['purchase'],

    'data': [
        'views/purchase_order.xml',
        'report/report_purchaseorder.xml',
    ],
}
