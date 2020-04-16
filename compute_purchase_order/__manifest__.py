{
    'name': 'Computed Purchase Order',
    'version': '11.0.1.0.0',
    'category': 'Purchase Order',
    'description': """ todo """,
    'author': 'Coop IT Easy',
    'website': 'https://github.com/coopiteasy/procurement-addons',
    'license': 'AGPL-3',
    'depends': [
        'product',
        'purchase',
        'stock',
        'stock_coverage',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/computed_purchase_order.xml',
        'views/purchase_order.xml',
    ],
}
