# Copyright 2020 Coop IT Easy SCRL fs
#   Elouan Le Bars <elouan@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


{
    "name": "Beescoop Shift Management",
    "summary": """Generate and manage shifts for cooperators.""",
    "author": "Thibault Francois, Elouan Le Bars, Coop IT Easy SCRLfs",
    "website": "https://github.com/beescoop/Obeesdoo",
    "category": "Cooperative management",
    "version": "12.0.1.1.0",
    "depends": ["beesdoo_base", "mail"],
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
        "wizard/instanciate_planning.xml",
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
