# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer Attendances",
    "summary": "Specify volunteers' type of absences",
    "version": "16.0.0.5.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "application": False,
    "depends": ["base", "volunteer", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/volunteer_shift_attendance_status_view.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [],
}
