{
    'name': "Beescoop Shift Management",

    'summary': """
        Volonteer Timetable Management""",

    'description': """

    """,

    'author': "Thibault Francois, Elouan Le Bars, Coop It Easy",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',
    'version': '11.0.1.0.0',

    'depends': ['beesdoo_base', 'barcodes'],

    'data': [
        "data/system_parameter.xml",
        "data/cron.xml",
        "data/mail_template.xml",
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
