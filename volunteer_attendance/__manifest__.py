# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer Attendances",
    "summary": "Specify volunteers' type of absences",
    "version": "16.0.0.5.1",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["remytms"],
    "license": "AGPL-3",
    "application": False,
    "depends": ["volunteer", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "security/volunteer_security.xml",
        "views/volunteer_shift_attendance_status_views.xml",
        "views/volunteer_menu.xml",
        "views/volunteer_shift_views.xml",
        "views/volunteer_volunteer_views.xml",
        "views/volunteer_shift_participation_views.xml",
    ],
    "demo": [
        "demo/volunteer_shift_attendance_status_demo.xml",
    ],
}
