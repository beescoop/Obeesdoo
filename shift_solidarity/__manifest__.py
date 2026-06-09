# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Solidarity",
    "summary": """
        Manage solidarity shifts: offer shift for other and request
        shifts.
    """,
    "author": "Coop IT Easy SC",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative Management",
    "version": "16.0.1.0.1",
    "depends": [
        "shift",
    ],
    "data": [
        "data/system_parameter.xml",
        "security/ir.model.access.csv",
        "views/res_config_setting_view.xml",
        "views/res_partner.xml",
        "views/shift_shift.xml",
        "views/shift_solidarity_menu.xml",
        "views/solidarity_shift_offer.xml",
        "views/solidarity_shift_request.xml",
    ],
    "demo": [],
    "license": "AGPL-3",
}
