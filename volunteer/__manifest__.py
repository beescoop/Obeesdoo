# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer",
    "summary": """
        Generate and manage shifts for volunteers.""",
    "version": "16.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["aydrpm"],
    "license": "AGPL-3",
    "application": True,
    "depends": [],
    "excludes": [],
    "data": [
        "security/volunteer_security.xml",
        "security/ir.model.access.csv",
        "views/shift_view.xml",
        "views/category_view.xml",
        "views/type_view.xml",
        "views/tag_view.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [
        "data/volunteer.shift.category.csv",
        "data/volunteer.shift.type.csv",
        "data/volunteer.shift.tag.csv",
    ],
    "qweb": [],
}
