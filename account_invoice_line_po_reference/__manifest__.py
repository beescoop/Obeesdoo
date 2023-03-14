# SPDX-FileCopyrightText: 2022 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Account Invoice Line PO Reference",
    "summary": """
        Allows to set the invoice line description from the
        related purchase order line.""",
    "version": "12.0.1.0.0",
    "category": "Account",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["victor-champonnois"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "account",
        "purchase",
    ],
    "excludes": [],
    "data": [
        "security/invoice_security.xml",
        "views/res_config_settings_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "pre_init_hook": "rename_security_group",
}
