{
    'name': "Beescoop link with easy my coop",

    'summary': """
        Module that made the link between beesdoo customization
        and easy_my_coop
    """,

    'description': """
    """,

    'author': "Beescoop - Cellule IT",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',
    'version': '12.0.1.0.0',

    'depends': ['beesdoo_base',
                'beesdoo_shift',
                'easy_my_coop',
                'easy_my_coop_eater',
                'easy_my_coop_website',
                ],

    'data': [
        'views/res_company.xml',
        'views/subscription_request.xml',
        'views/subscription_templates.xml',
        'views/product.xml'
    ],
    'demo': [
        'demo/product_share.xml',
    ],
    'auto_install': True,
}
