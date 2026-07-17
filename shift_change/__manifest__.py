# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Change",
    "summary": """
        Let regular workers change their shift.
    """,
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative Management",
    "version": "16.0.1.0.3",
    "depends": [
        "shift",
    ],
    "data": [
        "data/system_parameter.xml",
        "security/ir.model.access.csv",
        "views/shift_change.xml",
        "views/shift_change_menu.xml",
        "views/res_config_setting_view.xml",
        "views/res_partner.xml",
        "wizard/shift_change_create_wizard.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
}
