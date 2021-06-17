{
    "name": "BEES coop Shift Swap",
    "summary": """
    Allow workers to swap exchange shifts between each other.
    """,
    "author": "Coop It Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative Management",
    "version": "12.0.1.0.2",
    "license": "AGPL-3",
    "depends": ["beesdoo_shift"],
    "data": [
        "data/system_parameter.xml",
        "security/shift_swap_group.xml",
        "security/ir.model.access.csv",
        "views/shift_swap.xml",
        "views/shift_swap_subscribe.xml",
        "views/shift_swap_timeslot.xml",
        "views/res_config_setting_view.xml",
        "wizard/subscribe_shift_swap.xml",
        "wizard/exchange_wizard.xml",
    ],
    "demo": ["demo/demo.xml"],
}
