{
    'name': "Beesdoo Inventory",

    'summary': """
        Adds a responsible, a max shipping date and a button to copy quantity to
        stock pickings.""",

    'description': """

    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['delivery', 'beesdoo_base'],

    # always loaded
    'data': [
        'views/stock.xml'    ],

    # only loaded in demonstration mode
    'demo': [],
}
