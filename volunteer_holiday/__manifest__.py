# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Volunteer Holiday",
    "summary": "Add holidays for companies and volunteers",
    "version": "16.0.0.5.0",
    "category": "Volunteer management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["remytms"],
    "license": "AGPL-3",
    "application": False,
    "depends": ["base", "volunteer", "mail"],
    "data": [
        "data/cron.xml",
        "security/ir.model.access.csv",
        "security/volunteer_security.xml",
        "views/res_config_settings_views.xml",
        "views/volunteer_shift_generator_views.xml",
        "views/volunteer_company_holiday_view.xml",
        "views/volunteer_volunteer_view.xml",
        "views/volunteer_volunteer_leave_type_view.xml",
        "views/volunteer_volunteer_leave_view.xml",
        "views/volunteer_menu.xml",
    ],
    "demo": [
        "demo/volunteer_company_holiday_demo.xml",
        "demo/volunteer_volunteer_leave_type_demo.xml",
        "demo/volunteer_volunteer_leave_demo.xml",
    ],
}
