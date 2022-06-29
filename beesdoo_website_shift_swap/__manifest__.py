# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Beesdoo Website Shift Swap",
    "summary": """
        Add shift exchanges and solidarity shifts offers and requests.""",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "version": "12.0.1.0.2",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "depends": ["beesdoo_shift_swap", "beesdoo_website_shift"],
    "data": [
        "data/system_parameter.xml",
        "views/assets.xml",
        "views/exchange_templates.xml",
        "views/general_templates.xml",
        "views/solidarity_templates.xml",
        "views/swap_templates.xml",
        "views/res_config_settings_view.xml",
    ],
}
