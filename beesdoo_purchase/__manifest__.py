{
    'name': "Bees Purchase",

    'summary': """
        Extension du module Purchase""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Beescoop - Cellule IT, "
              "Coop IT Easy SCRLfs",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Purchase',
    'version': '12.0.1.1.0',

    'depends': ['base', 'purchase', 'beesdoo_product'],

    'data': [
        'views/purchase_order.xml',
        'security/ir.model.access.csv',
        'report/report_purchaseorder.xml',
    ],
}
