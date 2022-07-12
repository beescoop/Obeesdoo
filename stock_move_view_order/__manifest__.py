#coding:utf-8
{
    'name': "stock_move_view_order",

    'author': 'Polln group',

    'summary': """
    Module that reverses the order in function of dates in products
    """,

    'website': "https://github.com/beescoop/Obeesdo",
    'licence': "AGPL-3",

    'description': """
    """,

    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Extra tools',
    'version': '12.0.2.1.0',

    'sequence': '10',

    'depends': ['base', 'stock'],

    'data': [
        "views/inhereted_view_from_stock_move_line.xml"
    ],

    'installable': True,

    'application': True,

    'auto_install': False
}
