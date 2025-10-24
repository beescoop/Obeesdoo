# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer",
    "summary": """
        Generate and manage shifts for volunteers.""",
    "version": "16.0.0.3.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["aydrpm", "remytms"],
    "license": "AGPL-3",
    "application": True,
    "depends": ["mail"],
    "data": [
        "data/volunteer_shift_stage_data.xml",
        "security/volunteer_security.xml",
        "security/ir.model.access.csv",
        "views/volunteer_volunteer_views.xml",
        "views/volunteer_volunteer_kanban_views.xml",
        "views/volunteer_shift_views.xml",
        "views/volunteer_shift_generator_views.xml",
        "views/volunteer_shift_kanban_views.xml",
        "views/volunteer_shift_participation_views.xml",
        "views/volunteer_shift_subscription_views.xml",
        "views/volunteer_shift_category_views.xml",
        "views/volunteer_shift_type_views.xml",
        "views/volunteer_shift_tag_views.xml",
        "views/volunteer_skill_view.xml",
        "views/volunteer_skill_category_view.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [
        "demo/volunteer_shift_category_demo.xml",
        "demo/volunteer_shift_type_demo.xml",
        "demo/volunteer_shift_tag_demo.xml",
        "demo/volunteer_skill_category_demo.xml",
        "demo/volunteer_skill_demo.xml",
        "demo/volunteer_volunteer_demo.xml",
        "demo/volunteer_shift_demo.xml",
        "demo/volunteer_shift_participation_demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "volunteer/static/src/scss/volunteer_shift.scss",
        ],
    },
}
