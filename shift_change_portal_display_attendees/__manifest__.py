# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Change Portal Display Attendees",
    "summary": """
        Display registered attendee names and supercoop contact info
        in shift change selection modals on the portal.
    """,
    "version": "16.0.1.0.0",
    "category": "Cooperative management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "depends": [
        "shift_change_portal",
        "shift_portal_display_attendees",
    ],
    "data": [
        "views/templates.xml",
    ],
}
