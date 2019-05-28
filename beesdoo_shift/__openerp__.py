# -*- coding: utf-8 -*-
{
    'name': "Beescoop Shift Management",

    'summary': """
        Volonteer Timetable Management""",

    'description': """

    """,

    'author': "Thibault Francois",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',
    'version': '9.0.1.0.2',

    'depends': ['beesdoo_base'],

    'data': [
        "data/stage.xml",
        "data/system_parameter.xml",
        "data/cron.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/task_template.xml",
        "views/task.xml",
        "views/planning.xml",
        "views/cooperative_status.xml",
        "views/exempt_reason.xml",
        "wizard/instanciate_planning.xml",
        "wizard/batch_template.xml",
        "wizard/assign_super_coop.xml",
        "wizard/subscribe.xml",
        "wizard/extension.xml",
        "wizard/holiday.xml",
        "wizard/temporary_exemption.xml",
    ],
}
