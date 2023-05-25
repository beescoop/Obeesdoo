# Copyright 2020-2023 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Shift Management",
    "summary": """Generate and manage shifts for cooperators.""",
    "author": """
        Thibault Francois,
        Elouan Le Bars,
        Coop IT Easy SC,
        Odoo Community Association (OCA),
        """,
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "16.0.1.0.0",
    "depends": ["mail"],
    "data": [
        "data/system_parameter.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/task_template.xml",
        "views/task.xml",
        "views/planning.xml",
        "views/cooperative_status.xml",
        "views/exempt_reason.xml",
        "views/menu.xml",
        "views/res_config_settings_view.xml",
        "wizard/instantiate_planning.xml",
        "wizard/batch_template.xml",
        "wizard/assign_super_coop.xml",
        "wizard/subscribe.xml",
        "wizard/extension.xml",
        "wizard/holiday.xml",
        "wizard/temporary_exemption.xml",
    ],
    "demo": [
        "demo/exempt_reason.xml",
        "demo/workers.xml",
        "demo/templates.xml",
    ],
    "license": "AGPL-3",
}
