# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Change Portal",
    "summary": """
        Let regular workers change their shifts in the portal.""",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "version": "16.0.1.0.0",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "depends": ["shift_change", "shift_portal"],
    "data": [
        "data/system_parameter.xml",
        "views/my_shift_website_templates.xml",
        "views/change_templates.xml",
        "views/res_config_setting_view.xml",
    ],
}
