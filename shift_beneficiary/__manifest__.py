# SPDX-FileCopyrightText: 2023 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Beneficiary",
    "summary": """
        Add a 'beneficiary' field on shifts""",
    "version": "16.0.1.1.0",
    "category": "Cooperative management",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "shift",
        "shift_portal",
    ],
    "data": [
        "views/task.xml",
        "views/task_template.xml",
        "views/res_partner.xml",
        "views/shift_website_templates.xml",
    ],
    "demo": [],
    "qweb": [],
}
