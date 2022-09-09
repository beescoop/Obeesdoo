{
    "name": "Beescoop link with easy my coop",
    "summary": """Link between beesdoo customization and easy_my_coop""",
    "author": "BEES coop, Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "12.0.1.2.0",
    "depends": [
        "eater",
        "beesdoo_shift",
        "cooperator",
        "cooperator_website",
        "partner_contact_birthdate",
        # fixme: the module itself does not depend on member_card, but its
        # demo data and its tests do
        "member_card",
    ],
    "data": [
        "views/res_company.xml",
        "views/res_partner.xml",
        "views/subscription_request.xml",
        "views/subscription_templates.xml",
        "views/product.xml",
    ],
    "demo": ["demo/product_share.xml"],
    "auto_install": True,
    "license": "AGPL-3",
}
