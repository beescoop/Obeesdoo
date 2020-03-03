{
    'name': "Beescoop Shift Attendance Sheet",

    'summary': """
        Volonteer Timetable Management
        Attendance Sheet""",

    'description': """

    """,

    'author': "Elouan Le Bars, Coop It Easy",
    'website': "https://github.com/beescoop/Obeesdoo",

    'category': 'Cooperative management',
    'version': '12.0.1.0.0',

    'depends': [
        'beesdoo_shift',
        'beesdoo_worker_status', #TODO move the part that require beesdoo_worker_status in beesdoo_worker status or another module
        'mail',
        'barcodes',
    ],

    'data': [
        "data/system_parameter.xml",
        "data/cron.xml",
        "data/mail_template.xml",
        "security/group.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "wizard/validate_attendance_sheet.xml",
        "views/attendance_sheet.xml",
    ],
    'demo': []
}
