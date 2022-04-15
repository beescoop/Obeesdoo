{
    "name": "Beesdoo Website Shift Swap",
    "summary": """
        let workers to create exchange or swaping shift with an
        easy web interface.""",
    "author": "Coop IT Easy SCRLfs",
    "license": "AGPL-3",
    "version": "12.0.1.0.1",
    "website": "https://coopiteasy.be",
    "category": "Cooperative management",
    "depends": ["portal", "website", "beesdoo_shift", "beesdoo_shift_swap"],
    "data": [
        # 'security/ir.model.access.csv',
        "views/assets.xml",
        "views/exchange_templates.xml",
        "views/general_templates.xml",
        "views/solidarity_templates.xml",
        "views/swap_underpopulated_templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}