# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer",
    "summary": """
        Generate and manage shifts for volunteers.""",
    "version": "16.0.0.1.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["aydrpm", "remytms"],
    "license": "AGPL-3",
    "application": True,
    "depends": ["mail"],
    "data": [
        "data/shift_stage.xml",
        "security/volunteer_security.xml",
        "security/ir.model.access.csv",
        "views/volunteer_menu.xml",
        "views/shift_view.xml",
        "views/shift_kanban_view.xml",
        "views/volunteer_view.xml",
        "views/volunteer_kanban_view.xml",
        "views/shift_category_view.xml",
        "views/shift_type_view.xml",
        "views/shift_tag_view.xml",
    ],
    "demo": [
        "demo/shift_category_demo.xml",
        "demo/shift_type_demo.xml",
        "demo/shift_tag_demo.xml",
        "demo/volunteer_demo.xml",
        "demo/shift_demo.xml",
        "demo/shift_participation_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "volunteer/static/src/scss/volunteer_shift.scss",
        ],
    },
}
