{
    "name": "Beesdoo Website Shift Swap",
    "summary": """
        Add shift exchanges and solidarity shifts offers and requests.""",
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "version": "12.0.1.0.1",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "depends": ["beesdoo_shift_swap", "beesdoo_website_shift"],
    "data": [
        # 'security/ir.model.access.csv',
        "views/assets.xml",
        "views/exchange_templates.xml",
        "views/general_templates.xml",
        "views/solidarity_templates.xml",
        "views/swap_templates.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
