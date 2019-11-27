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
    'version': '9.0.1.3.0',

    'depends': ['beesdoo_base', 'barcodes'],

    'data': [
        "data/stage.xml",
        "data/system_parameter.xml",
        "data/cron.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/task_template.xml",
        "views/res_config_view.xml",
        "views/task.xml",
        "views/planning.xml",
        "views/cooperative_status.xml",
        "views/exempt_reason.xml",
        "wizard/validate_attendance_sheet.xml",
        "views/attendance_sheet.xml",
        "views/attendance_sheet_admin.xml",
        "wizard/instanciate_planning.xml",
        "wizard/batch_template.xml",
        "wizard/assign_super_coop.xml",
        "wizard/subscribe.xml",
        "wizard/extension.xml",
        "wizard/holiday.xml",
        "wizard/temporary_exemption.xml",
    ],
    'demo': [
        "demo/workers.xml",
        "demo/users.xml",
        "demo/templates.xml",
    ]
}
