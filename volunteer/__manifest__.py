# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer",
    "summary": """
        Generate and manage shifts for volunteers.""",
    "version": "16.0.1.0.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["aydrpm"],
    "license": "AGPL-3",
    "application": True,
    "depends": ["mail"],
    "excludes": [],
    "data": [
        "security/volunteer_security.xml",
        "security/ir.model.access.csv",
        "views/shift_view.xml",
        "views/volunteer_view.xml",
        "views/shift_participation.xml",
        "views/shift_category_view.xml",
        "views/shift_type_view.xml",
        "views/shift_tag_view.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [
        "demo/shift_category_demo.xml",
        "demo/shift_type_demo.xml",
        "demo/shift_tag_demo.xml",
    ],
    "qweb": [],
}
