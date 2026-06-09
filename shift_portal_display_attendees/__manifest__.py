# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Portal Display Attendees",
    "summary": """
        Display registered attendee names and supercoop contact info
        in shift subscription modals on the portal.
    """,
    "version": "16.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "depends": [
        "shift_portal",
    ],
    "data": [
        "views/res_config_views.xml",
        "views/templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "shift_portal_display_attendees/static/src/css/display_attendees.css",
        ],
    },
}
