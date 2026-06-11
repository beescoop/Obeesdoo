# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Shift Solidarity Portal",
    "summary": """
        Let workers offer or request a solidarity shift in the portal.""",
    "author": "Coop IT Easy SC",
    "license": "AGPL-3",
    "version": "12.0.1.0.0",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "depends": ["shift_solidarity", "beesdoo_website_shift"],
    "data": [
        "views/my_shift_website_templates.xml",
        "views/solidarity_templates.xml",
    ],
}
