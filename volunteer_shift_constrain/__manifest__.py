# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer Shift Constrain",
    "summary": """
        Manage constrain that apply on shifts or shift type. Constrain
        allow to set rules to assign volunteer on a shift.""",
    "version": "16.0.0.1.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["remytms"],
    "license": "AGPL-3",
    "application": True,
    "depends": ["volunteer", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/volunteer_shift_constrain_views.xml",
        "views/volunteer_shift_type_views.xml",
        "views/volunteer_shift_views.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [
        "demo/volunteer_shift_constrain_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [],
    },
}
